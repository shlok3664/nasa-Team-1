"""Typed application service registry."""

from threading import RLock
from typing import TypeVar, cast

T = TypeVar("T")


class ServiceRegistry:
    """Registers and resolves shared application services."""

    def __init__(self) -> None:
        self._services: dict[type[object], object] = {}
        self._lock = RLock()

    def register(self, service_type: type[T], instance: T) -> None:
        """Register a service instance under its declared type."""

        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type")

        if not isinstance(instance, service_type):
            raise TypeError("service instance must match the registered service type")

        with self._lock:
            if service_type in self._services:
                raise ValueError(f"service is already registered: {service_type.__name__}")

            self._services[service_type] = instance

    def unregister(self, service_type: type[object]) -> bool:
        """Remove a registered service and report whether it existed."""

        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type")

        with self._lock:
            return self._services.pop(service_type, None) is not None

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a registered service or raise an error."""

        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type")

        with self._lock:
            if service_type not in self._services:
                raise KeyError(f"service is not registered: {service_type.__name__}")

            instance = self._services[service_type]

        return cast(T, instance)

    def get(self, service_type: type[T]) -> T | None:
        """Resolve a service, returning None when it is not registered."""

        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type")

        with self._lock:
            instance = self._services.get(service_type)

        if instance is None:
            return None

        return cast(T, instance)

    def is_registered(self, service_type: type[object]) -> bool:
        """Check whether a service type has been registered."""

        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type")

        with self._lock:
            return service_type in self._services

    @property
    def service_count(self) -> int:
        """Return the number of registered service types."""

        with self._lock:
            return len(self._services)
