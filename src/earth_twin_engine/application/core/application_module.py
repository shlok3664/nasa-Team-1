"""Base contract for application modules."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from earth_twin_engine.application.core.module_metadata import ModuleMetadata

if TYPE_CHECKING:
    from earth_twin_engine.application.core.application_context import (
        ApplicationContext,
    )


class ApplicationModule(ABC):
    """Defines the lifecycle contract shared by application modules.

    Concrete modules implement their own initialization, execution,
    update, stopping, and cleanup behavior.
    """

    @property
    @abstractmethod
    def metadata(self) -> ModuleMetadata:
        """Return the module's immutable metadata."""

    @abstractmethod
    def initialize(self, context: ApplicationContext) -> None:
        """Initialize the module using the shared application context."""

    @abstractmethod
    def start(self) -> None:
        """Start module execution."""

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Advance the module using elapsed time in seconds."""

    @abstractmethod
    def stop(self) -> None:
        """Stop module execution without releasing all resources."""

    @abstractmethod
    def shutdown(self) -> None:
        """Release module resources and complete its lifecycle."""
