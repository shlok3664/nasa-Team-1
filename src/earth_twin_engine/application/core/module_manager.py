"""Application module registration and lifecycle orchestration."""

from math import isfinite

from earth_twin_engine.application.core.application_context import (
    ApplicationContext,
)
from earth_twin_engine.application.core.application_module import (
    ApplicationModule,
)
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.core.module_state import ModuleState


class ModuleLifecycleError(RuntimeError):
    """Raised when an application module fails during its lifecycle."""

    def __init__(self, module_id: str, operation: str) -> None:
        self.module_id = module_id
        self.operation = operation
        super().__init__(f"Module '{module_id}' failed during {operation}")


class ModuleManager:
    """Coordinates registration, dependencies, and module lifecycles."""

    def __init__(self) -> None:
        self._modules: dict[str, ApplicationModule] = {}
        self._states: dict[str, ModuleState] = {}
        self._initialization_order: tuple[str, ...] = ()
        self._lifecycle_started = False

    def register(self, module: ApplicationModule) -> None:
        """Register a module before lifecycle execution begins."""

        if self._lifecycle_started:
            raise RuntimeError("modules cannot be registered after lifecycle execution begins")

        if not isinstance(module, ApplicationModule):
            raise TypeError("module must implement ApplicationModule")

        metadata = module.metadata

        if not isinstance(metadata, ModuleMetadata):
            raise TypeError("module metadata must be a ModuleMetadata")

        module_id = metadata.module_id

        if module_id in self._modules:
            raise ValueError(f"module is already registered: {module_id}")

        self._modules[module_id] = module
        self._states[module_id] = ModuleState.REGISTERED

    def get_module(self, module_id: str) -> ApplicationModule:
        """Retrieve a registered module by its identifier."""

        if module_id not in self._modules:
            raise KeyError(f"module is not registered: {module_id}")

        return self._modules[module_id]

    def get_state(self, module_id: str) -> ModuleState:
        """Retrieve the current lifecycle state of a module."""

        if module_id not in self._states:
            raise KeyError(f"module is not registered: {module_id}")

        return self._states[module_id]

    @property
    def module_count(self) -> int:
        """Return the number of registered modules."""

        return len(self._modules)

    @property
    def initialization_order(self) -> tuple[str, ...]:
        """Return the resolved dependency-safe module order."""

        return self._initialization_order

    def resolve_initialization_order(self) -> tuple[str, ...]:
        """Calculate a topological ordering of registered modules."""

        resolved: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(module_id: str) -> None:
            if module_id in visited:
                return

            if module_id in visiting:
                raise ValueError(f"circular module dependency detected at: {module_id}")

            module = self._modules[module_id]
            visiting.add(module_id)

            for dependency in module.metadata.dependencies:
                if dependency not in self._modules:
                    raise ValueError(
                        f"module '{module_id}' depends on unregistered module '{dependency}'"
                    )

                visit(dependency)

            visiting.remove(module_id)
            visited.add(module_id)
            resolved.append(module_id)

        for module_id in self._modules:
            visit(module_id)

        self._initialization_order = tuple(resolved)
        return self._initialization_order

    def initialize_all(self, context: ApplicationContext) -> None:
        """Initialize modules in dependency-safe order."""

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        if self._lifecycle_started:
            raise RuntimeError("module initialization has already begun")

        order = self.resolve_initialization_order()
        self._lifecycle_started = True

        for module_id in order:
            module = self._modules[module_id]

            try:
                module.initialize(context)
            except Exception as error:
                self._states[module_id] = ModuleState.FAILED
                raise ModuleLifecycleError(
                    module_id,
                    "initialization",
                ) from error

            self._states[module_id] = ModuleState.INITIALIZED

    def start_all(self) -> None:
        """Start all initialized modules in dependency-safe order."""

        if not self._lifecycle_started:
            raise RuntimeError("modules must be initialized before starting")

        for module_id in self._initialization_order:
            state = self._states[module_id]

            if state not in (
                ModuleState.INITIALIZED,
                ModuleState.STOPPED,
            ):
                raise RuntimeError(f"module '{module_id}' cannot start from state '{state.value}'")

            try:
                self._modules[module_id].start()
            except Exception as error:
                self._states[module_id] = ModuleState.FAILED
                raise ModuleLifecycleError(
                    module_id,
                    "start",
                ) from error

            self._states[module_id] = ModuleState.RUNNING

    def update_all(self, delta_time: float) -> None:
        """Update running modules with elapsed time in seconds."""

        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be numeric")

        if not isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be finite and non-negative")

        running_modules = [
            module_id
            for module_id in self._initialization_order
            if self._states[module_id] is ModuleState.RUNNING
        ]

        if not self._initialization_order:
            return

        if not running_modules:
            raise RuntimeError("there are no running modules to update")

        for module_id in running_modules:
            try:
                self._modules[module_id].update(float(delta_time))
            except Exception as error:
                self._states[module_id] = ModuleState.FAILED
                raise ModuleLifecycleError(
                    module_id,
                    "update",
                ) from error

    def stop_all(self) -> None:
        """Stop running modules in reverse dependency order."""

        if not self._lifecycle_started:
            raise RuntimeError("modules have not been initialized")

        for module_id in reversed(self._initialization_order):
            if self._states[module_id] is not ModuleState.RUNNING:
                continue

            try:
                self._modules[module_id].stop()
            except Exception as error:
                self._states[module_id] = ModuleState.FAILED
                raise ModuleLifecycleError(
                    module_id,
                    "stop",
                ) from error

            self._states[module_id] = ModuleState.STOPPED

    def shutdown_all(self) -> None:
        """Shut down modules in reverse dependency order."""

        if not self._lifecycle_started:
            raise RuntimeError("modules have not been initialized")

        self.stop_all()

        for module_id in reversed(self._initialization_order):
            if self._states[module_id] not in (
                ModuleState.INITIALIZED,
                ModuleState.STOPPED,
            ):
                continue

            try:
                self._modules[module_id].shutdown()
            except Exception as error:
                self._states[module_id] = ModuleState.FAILED
                raise ModuleLifecycleError(
                    module_id,
                    "shutdown",
                ) from error

            self._states[module_id] = ModuleState.SHUTDOWN
