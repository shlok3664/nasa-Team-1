"""Tests for application module management."""

import pytest

from earth_twin_engine.application.core import (
    ApplicationConfiguration,
    ApplicationContext,
    ApplicationModule,
    ModuleLifecycleError,
    ModuleManager,
    ModuleMetadata,
    ModuleState,
    ServiceRegistry,
)


class ExampleModule(ApplicationModule):
    """Test module with observable lifecycle operations."""

    def __init__(
        self,
        module_id: str,
        dependencies: tuple[str, ...] = (),
        fail_on: str | None = None,
        execution_log: list[str] | None = None,
    ) -> None:
        self._metadata = ModuleMetadata(
            module_id=module_id,
            name=module_id.replace("_", " ").title(),
            version="1.0.0",
            dependencies=dependencies,
        )
        self.fail_on = fail_on
        self.execution_log = execution_log if execution_log is not None else []
        self.update_deltas: list[float] = []

    @property
    def metadata(self) -> ModuleMetadata:
        return self._metadata

    def _execute(self, operation: str) -> None:
        self.execution_log.append(f"{operation}:{self._metadata.module_id}")

        if self.fail_on == operation:
            raise RuntimeError(f"Simulated {operation} failure")

    def initialize(self, context: ApplicationContext) -> None:
        self._execute("initialize")

    def start(self) -> None:
        self._execute("start")

    def update(self, delta_time: float) -> None:
        self._execute("update")
        self.update_deltas.append(delta_time)

    def stop(self) -> None:
        self._execute("stop")

    def shutdown(self) -> None:
        self._execute("shutdown")


@pytest.fixture
def context() -> ApplicationContext:
    return ApplicationContext(
        configuration=ApplicationConfiguration(
            application_name="Earth Twin Engine",
            environment="testing",
        ),
        services=ServiceRegistry(),
    )


def test_register_module() -> None:
    manager = ModuleManager()
    module = ExampleModule("time_series")

    manager.register(module)

    assert manager.module_count == 1
    assert manager.get_module("time_series") is module
    assert manager.get_state("time_series") is ModuleState.REGISTERED


def test_reject_duplicate_module_registration() -> None:
    manager = ModuleManager()

    manager.register(ExampleModule("time_series"))

    with pytest.raises(ValueError, match="already registered"):
        manager.register(ExampleModule("time_series"))


def test_reject_non_application_module() -> None:
    manager = ModuleManager()

    with pytest.raises(TypeError, match="ApplicationModule"):
        manager.register(object())  # type: ignore[arg-type]


def test_reject_module_with_invalid_metadata() -> None:
    class InvalidMetadataModule(ExampleModule):
        @property
        def metadata(self) -> ModuleMetadata:
            return None  # type: ignore[return-value]

    manager = ModuleManager()

    with pytest.raises(TypeError, match="ModuleMetadata"):
        manager.register(InvalidMetadataModule("invalid_module"))


def test_retrieve_unregistered_module() -> None:
    manager = ModuleManager()

    with pytest.raises(KeyError, match="not registered"):
        manager.get_module("missing_module")


def test_retrieve_unregistered_module_state() -> None:
    manager = ModuleManager()

    with pytest.raises(KeyError, match="not registered"):
        manager.get_state("missing_module")


def test_resolve_initialization_order() -> None:
    manager = ModuleManager()

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
        )
    )
    manager.register(
        ExampleModule(
            "time_series",
            dependencies=("data_acquisition",),
        )
    )
    manager.register(ExampleModule("data_acquisition"))

    order = manager.resolve_initialization_order()

    assert order.index("data_acquisition") < order.index("time_series")
    assert order.index("time_series") < order.index("trend_analysis")


def test_resolve_independent_modules() -> None:
    manager = ModuleManager()

    manager.register(ExampleModule("data_acquisition"))
    manager.register(ExampleModule("visualization"))

    assert manager.resolve_initialization_order() == (
        "data_acquisition",
        "visualization",
    )


def test_reject_missing_dependency() -> None:
    manager = ModuleManager()

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
        )
    )

    with pytest.raises(ValueError, match="unregistered module"):
        manager.resolve_initialization_order()


def test_reject_circular_dependencies() -> None:
    manager = ModuleManager()

    manager.register(ExampleModule("module_a", dependencies=("module_b",)))
    manager.register(ExampleModule("module_b", dependencies=("module_a",)))

    with pytest.raises(ValueError, match="circular"):
        manager.resolve_initialization_order()


def test_initialize_modules_in_dependency_order(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    execution_log: list[str] = []

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
            execution_log=execution_log,
        )
    )
    manager.register(
        ExampleModule(
            "time_series",
            dependencies=("data_acquisition",),
            execution_log=execution_log,
        )
    )
    manager.register(
        ExampleModule(
            "data_acquisition",
            execution_log=execution_log,
        )
    )

    manager.initialize_all(context)

    assert execution_log == [
        "initialize:data_acquisition",
        "initialize:time_series",
        "initialize:trend_analysis",
    ]

    assert manager.get_state("data_acquisition") is ModuleState.INITIALIZED
    assert manager.get_state("time_series") is ModuleState.INITIALIZED
    assert manager.get_state("trend_analysis") is ModuleState.INITIALIZED


def test_reject_invalid_application_context() -> None:
    manager = ModuleManager()

    with pytest.raises(TypeError, match="ApplicationContext"):
        manager.initialize_all(object())  # type: ignore[arg-type]


def test_reject_initialization_when_already_started(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series"))

    manager.initialize_all(context)

    with pytest.raises(RuntimeError, match="already begun"):
        manager.initialize_all(context)


def test_reject_registration_after_initialization(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series"))
    manager.initialize_all(context)

    with pytest.raises(RuntimeError, match="cannot be registered"):
        manager.register(ExampleModule("visualization"))


def test_module_initialization_failure_marks_module_failed(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("data_acquisition", fail_on="initialize"))

    with pytest.raises(ModuleLifecycleError) as error:
        manager.initialize_all(context)

    assert error.value.module_id == "data_acquisition"
    assert error.value.operation == "initialization"
    assert manager.get_state("data_acquisition") is ModuleState.FAILED
    assert isinstance(error.value.__cause__, RuntimeError)


def test_initialization_failure_prevents_dependent_initialization(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    execution_log: list[str] = []

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
            execution_log=execution_log,
        )
    )
    manager.register(
        ExampleModule(
            "time_series",
            fail_on="initialize",
            execution_log=execution_log,
        )
    )

    with pytest.raises(ModuleLifecycleError):
        manager.initialize_all(context)

    assert execution_log == ["initialize:time_series"]
    assert manager.get_state("trend_analysis") is ModuleState.REGISTERED


def test_start_modules_in_dependency_order(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    execution_log: list[str] = []

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
            execution_log=execution_log,
        )
    )
    manager.register(ExampleModule("time_series", execution_log=execution_log))

    manager.initialize_all(context)
    manager.start_all()

    assert execution_log == [
        "initialize:time_series",
        "initialize:trend_analysis",
        "start:time_series",
        "start:trend_analysis",
    ]

    assert manager.get_state("time_series") is ModuleState.RUNNING
    assert manager.get_state("trend_analysis") is ModuleState.RUNNING


def test_reject_start_before_initialization() -> None:
    manager = ModuleManager()

    with pytest.raises(RuntimeError, match="initialized"):
        manager.start_all()


def test_module_start_failure_marks_module_failed(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series", fail_on="start"))
    manager.initialize_all(context)

    with pytest.raises(ModuleLifecycleError) as error:
        manager.start_all()

    assert error.value.operation == "start"
    assert manager.get_state("time_series") is ModuleState.FAILED


def test_update_running_modules(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    first = ExampleModule("data_acquisition")
    second = ExampleModule(
        "trend_analysis",
        dependencies=("data_acquisition",),
    )

    manager.register(first)
    manager.register(second)
    manager.initialize_all(context)
    manager.start_all()

    manager.update_all(0.016)

    assert first.update_deltas == [pytest.approx(0.016)]
    assert second.update_deltas == [pytest.approx(0.016)]


@pytest.mark.parametrize(
    "delta_time",
    [
        -0.1,
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_reject_invalid_delta_time(
    context: ApplicationContext,
    delta_time: float,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series"))
    manager.initialize_all(context)
    manager.start_all()

    with pytest.raises(ValueError, match="delta_time"):
        manager.update_all(delta_time)


def test_reject_non_numeric_delta_time(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series"))
    manager.initialize_all(context)
    manager.start_all()

    with pytest.raises(TypeError, match="numeric"):
        manager.update_all("0.016")  # type: ignore[arg-type]


def test_reject_update_when_no_modules_are_running(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series"))
    manager.initialize_all(context)

    with pytest.raises(RuntimeError, match="no running modules"):
        manager.update_all(0.016)


def test_update_failure_marks_module_failed(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series", fail_on="update"))
    manager.initialize_all(context)
    manager.start_all()

    with pytest.raises(ModuleLifecycleError) as error:
        manager.update_all(0.016)

    assert error.value.operation == "update"
    assert manager.get_state("time_series") is ModuleState.FAILED


def test_stop_modules_in_reverse_dependency_order(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    execution_log: list[str] = []

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
            execution_log=execution_log,
        )
    )
    manager.register(ExampleModule("time_series", execution_log=execution_log))

    manager.initialize_all(context)
    manager.start_all()
    execution_log.clear()

    manager.stop_all()

    assert execution_log == [
        "stop:trend_analysis",
        "stop:time_series",
    ]

    assert manager.get_state("trend_analysis") is ModuleState.STOPPED
    assert manager.get_state("time_series") is ModuleState.STOPPED


def test_stopped_modules_can_be_restarted(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series"))

    manager.initialize_all(context)
    manager.start_all()
    manager.stop_all()
    manager.start_all()

    assert manager.get_state("time_series") is ModuleState.RUNNING


def test_shutdown_modules_in_reverse_dependency_order(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    execution_log: list[str] = []

    manager.register(
        ExampleModule(
            "trend_analysis",
            dependencies=("time_series",),
            execution_log=execution_log,
        )
    )
    manager.register(ExampleModule("time_series", execution_log=execution_log))

    manager.initialize_all(context)
    manager.start_all()
    execution_log.clear()

    manager.shutdown_all()

    assert execution_log == [
        "stop:trend_analysis",
        "stop:time_series",
        "shutdown:trend_analysis",
        "shutdown:time_series",
    ]

    assert manager.get_state("trend_analysis") is ModuleState.SHUTDOWN
    assert manager.get_state("time_series") is ModuleState.SHUTDOWN


def test_shutdown_initialized_modules_without_starting(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    module = ExampleModule("time_series")

    manager.register(module)
    manager.initialize_all(context)
    manager.shutdown_all()

    assert manager.get_state("time_series") is ModuleState.SHUTDOWN


def test_reject_stop_before_initialization() -> None:
    manager = ModuleManager()

    with pytest.raises(RuntimeError, match="not been initialized"):
        manager.stop_all()


def test_reject_shutdown_before_initialization() -> None:
    manager = ModuleManager()

    with pytest.raises(RuntimeError, match="not been initialized"):
        manager.shutdown_all()


def test_module_stop_failure_marks_module_failed(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series", fail_on="stop"))
    manager.initialize_all(context)
    manager.start_all()

    with pytest.raises(ModuleLifecycleError) as error:
        manager.stop_all()

    assert error.value.operation == "stop"
    assert manager.get_state("time_series") is ModuleState.FAILED


def test_module_shutdown_failure_marks_module_failed(
    context: ApplicationContext,
) -> None:
    manager = ModuleManager()
    manager.register(ExampleModule("time_series", fail_on="shutdown"))
    manager.initialize_all(context)

    with pytest.raises(ModuleLifecycleError) as error:
        manager.shutdown_all()

    assert error.value.operation == "shutdown"
    assert manager.get_state("time_series") is ModuleState.FAILED
