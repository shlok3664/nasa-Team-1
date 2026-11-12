"""Coordinates the lifecycle of the application."""

import math

from earth_twin_engine.application.core.application_context import (
    ApplicationContext,
)
from earth_twin_engine.application.core.module_manager import ModuleManager
from earth_twin_engine.application.resource_management import (
    ResourceCleanupFailure,
    ResourceManager,
)
from earth_twin_engine.application.runtime.runtime_state import RuntimeState


class ApplicationRuntime:
    """Coordinates module execution and application resource cleanup."""

    def __init__(
        self,
        module_manager: ModuleManager,
        context: ApplicationContext,
        resource_manager: ResourceManager | None = None,
    ) -> None:
        if not isinstance(module_manager, ModuleManager):
            raise TypeError("module_manager must be a ModuleManager")

        if not isinstance(context, ApplicationContext):
            raise TypeError("context must be an ApplicationContext")

        if resource_manager is not None and not isinstance(resource_manager, ResourceManager):
            raise TypeError("resource_manager must be a ResourceManager or None")

        self._module_manager = module_manager
        self._context = context
        self._resource_manager = (
            resource_manager if resource_manager is not None else ResourceManager()
        )
        self._state = RuntimeState.CREATED
        self._modules_initialized = False
        self._cleanup_failures: tuple[ResourceCleanupFailure, ...] = ()

    @property
    def state(self) -> RuntimeState:
        """Current runtime lifecycle state."""
        return self._state

    @property
    def context(self) -> ApplicationContext:
        """Application context shared with modules."""
        return self._context

    @property
    def cleanup_failures(self) -> tuple[ResourceCleanupFailure, ...]:
        """Resource cleanup failures encountered during shutdown."""
        return self._cleanup_failures

    def initialize(self) -> None:
        """Initialize all registered application modules."""

        self._require_state(RuntimeState.CREATED)

        try:
            self._module_manager.initialize_all(self._context)
            self._modules_initialized = True
        except Exception:
            self._state = RuntimeState.FAILED
            raise

        self._state = RuntimeState.INITIALIZED

    def start(self) -> None:
        """Start all initialized application modules."""

        self._require_state(RuntimeState.INITIALIZED)

        try:
            self._module_manager.start_all()
        except Exception:
            self._state = RuntimeState.FAILED
            raise

        self._state = RuntimeState.RUNNING

    def update(self, delta_time: float) -> None:
        """Update running modules using elapsed time in seconds."""

        self._require_state(RuntimeState.RUNNING)

        if isinstance(delta_time, bool) or not isinstance(delta_time, (int, float)):
            raise TypeError("delta_time must be a number")

        if not math.isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be finite and non-negative")

        try:
            self._module_manager.update_all(float(delta_time))
        except Exception:
            self._state = RuntimeState.FAILED
            raise

    def stop(self) -> None:
        """Stop all running application modules."""

        self._require_state(RuntimeState.RUNNING)

        try:
            self._module_manager.stop_all()
        except Exception:
            self._state = RuntimeState.FAILED
            raise

        self._state = RuntimeState.STOPPED

    def shutdown(self) -> None:
        """Shut down initialized modules and release registered resources."""

        if self._state is RuntimeState.SHUTDOWN:
            return

        errors: list[Exception] = []

        if self._state is RuntimeState.RUNNING:
            try:
                self._module_manager.stop_all()
            except Exception as exception:
                errors.append(exception)

        if self._modules_initialized:
            try:
                self._module_manager.shutdown_all()
            except Exception as exception:
                errors.append(exception)

        self._cleanup_failures = self._resource_manager.shutdown()
        self._state = RuntimeState.SHUTDOWN

        if errors:
            raise errors[0]

    def _require_state(self, expected: RuntimeState) -> None:
        if self._state is not expected:
            raise RuntimeError(
                f"Operation requires runtime state '{expected.value}', "
                f"but current state is '{self._state.value}'"
            )
