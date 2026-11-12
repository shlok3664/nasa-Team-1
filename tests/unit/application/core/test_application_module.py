"""Tests for the application module lifecycle contract."""

import pytest

from earth_twin_engine.application.core import (
    ApplicationModule,
    ModuleMetadata,
)


class ExampleModule(ApplicationModule):
    """Concrete test implementation of the module contract."""

    def __init__(self) -> None:
        self._metadata = ModuleMetadata(
            module_id="example_module",
            name="Example Module",
            version="1.0.0",
        )
        self.initialized = False
        self.started = False
        self.updated_delta: float | None = None
        self.stopped = False
        self.shutdown_called = False

    @property
    def metadata(self) -> ModuleMetadata:
        return self._metadata

    def initialize(self, context: object) -> None:
        self.initialized = True

    def start(self) -> None:
        self.started = True

    def update(self, delta_time: float) -> None:
        self.updated_delta = delta_time

    def stop(self) -> None:
        self.stopped = True

    def shutdown(self) -> None:
        self.shutdown_called = True


def test_application_module_is_abstract() -> None:
    with pytest.raises(TypeError, match="abstract"):
        ApplicationModule()  # type: ignore[abstract]


def test_concrete_module_implements_metadata_contract() -> None:
    module = ExampleModule()

    assert isinstance(module.metadata, ModuleMetadata)
    assert module.metadata.module_id == "example_module"


def test_module_initialization_hook() -> None:
    module = ExampleModule()

    module.initialize(object())

    assert module.initialized is True


def test_module_start_hook() -> None:
    module = ExampleModule()

    module.start()

    assert module.started is True


def test_module_update_hook() -> None:
    module = ExampleModule()

    module.update(0.016)

    assert module.updated_delta == pytest.approx(0.016)


def test_module_stop_hook() -> None:
    module = ExampleModule()

    module.stop()

    assert module.stopped is True


def test_module_shutdown_hook() -> None:
    module = ExampleModule()

    module.shutdown()

    assert module.shutdown_called is True


def test_module_supports_complete_lifecycle_sequence() -> None:
    module = ExampleModule()

    module.initialize(object())
    module.start()
    module.update(0.016)
    module.stop()
    module.shutdown()

    assert module.initialized is True
    assert module.started is True
    assert module.updated_delta == pytest.approx(0.016)
    assert module.stopped is True
    assert module.shutdown_called is True
