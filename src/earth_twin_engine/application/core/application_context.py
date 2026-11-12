"""Shared application context."""

from dataclasses import dataclass

from earth_twin_engine.application.core.application_configuration import (
    ApplicationConfiguration,
)
from earth_twin_engine.application.core.service_registry import ServiceRegistry


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Provides modules with access to shared application infrastructure."""

    configuration: ApplicationConfiguration
    services: ServiceRegistry

    def __post_init__(self) -> None:
        if not isinstance(self.configuration, ApplicationConfiguration):
            raise TypeError("configuration must be an ApplicationConfiguration")

        if not isinstance(self.services, ServiceRegistry):
            raise TypeError("services must be a ServiceRegistry")

    def resolve(self, service_type: type) -> object:
        """Resolve a shared application service."""

        return self.services.resolve(service_type)

    def get_service(self, service_type: type) -> object | None:
        """Retrieve a shared service when it is available."""

        return self.services.get(service_type)
