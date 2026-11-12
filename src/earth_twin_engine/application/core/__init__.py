"""Application core contracts and infrastructure."""

from earth_twin_engine.application.core.application_configuration import (
    ApplicationConfiguration,
)
from earth_twin_engine.application.core.application_context import (
    ApplicationContext,
)
from earth_twin_engine.application.core.application_module import (
    ApplicationModule,
)
from earth_twin_engine.application.core.module_manager import (
    ModuleLifecycleError,
    ModuleManager,
)
from earth_twin_engine.application.core.module_metadata import ModuleMetadata
from earth_twin_engine.application.core.module_state import ModuleState
from earth_twin_engine.application.core.service_registry import ServiceRegistry

__all__ = [
    "ApplicationConfiguration",
    "ApplicationContext",
    "ApplicationModule",
    "ModuleLifecycleError",
    "ModuleManager",
    "ModuleMetadata",
    "ModuleState",
    "ServiceRegistry",
]
