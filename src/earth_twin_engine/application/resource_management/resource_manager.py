"""Centralized lifecycle management for application resources."""

from collections.abc import Callable
from threading import RLock
from typing import TypeVar, cast

from earth_twin_engine.application.resource_management.resource_cleanup_failure import (
    ResourceCleanupFailure,
)

T = TypeVar("T")


class ResourceManager:
    """Registers, retrieves, releases, and cleans up application resources."""

    def __init__(self) -> None:
        self._resources: dict[str, object] = {}
        self._cleanup_callbacks: dict[str, Callable[[object], None]] = {}
        self._registration_order: list[str] = []
        self._lock = RLock()
        self._is_shutdown = False

    @property
    def is_shutdown(self) -> bool:
        """Whether the resource manager has been shut down."""
        with self._lock:
            return self._is_shutdown

    @property
    def resource_count(self) -> int:
        """Number of currently registered resources."""
        with self._lock:
            return len(self._resources)

    def register(
        self,
        resource_id: str,
        resource: T,
        cleanup: Callable[[T], None],
    ) -> None:
        """Register a resource with its explicit cleanup callback."""

        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")

        if resource is None:
            raise ValueError("resource cannot be None")

        if not callable(cleanup):
            raise TypeError("cleanup must be callable")

        with self._lock:
            if self._is_shutdown:
                raise RuntimeError("Cannot register resources after shutdown")

            if resource_id in self._resources:
                raise ValueError(f"Resource already registered: {resource_id}")

            self._resources[resource_id] = resource
            self._cleanup_callbacks[resource_id] = cast(
                Callable[[object], None],
                cleanup,
            )
            self._registration_order.append(resource_id)

    def resolve(self, resource_id: str) -> object:
        """Retrieve a registered resource by its identifier."""

        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")

        with self._lock:
            try:
                return self._resources[resource_id]
            except KeyError:
                raise KeyError(f"Resource is not registered: {resource_id}") from None

    def get(self, resource_id: str) -> object | None:
        """Retrieve a resource, returning None when it is not registered."""

        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")

        with self._lock:
            return self._resources.get(resource_id)

    def release(self, resource_id: str) -> ResourceCleanupFailure | None:
        """Remove and clean up one resource."""

        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")

        with self._lock:
            if self._is_shutdown:
                raise RuntimeError("Cannot release resources after shutdown")

            if resource_id not in self._resources:
                raise KeyError(f"Resource is not registered: {resource_id}")

            resource = self._resources.pop(resource_id)
            cleanup = self._cleanup_callbacks.pop(resource_id)
            self._registration_order.remove(resource_id)

        try:
            cleanup(resource)
        except Exception as exception:
            return ResourceCleanupFailure(
                resource_id=resource_id,
                exception=exception,
            )

        return None

    def shutdown(self) -> tuple[ResourceCleanupFailure, ...]:
        """Clean up all resources in reverse registration order."""

        with self._lock:
            if self._is_shutdown:
                return ()

            self._is_shutdown = True

            resources = [
                (
                    resource_id,
                    self._resources[resource_id],
                    self._cleanup_callbacks[resource_id],
                )
                for resource_id in reversed(self._registration_order)
            ]

            self._resources.clear()
            self._cleanup_callbacks.clear()
            self._registration_order.clear()

        failures: list[ResourceCleanupFailure] = []

        for resource_id, resource, cleanup in resources:
            try:
                cleanup(resource)
            except Exception as exception:
                failures.append(
                    ResourceCleanupFailure(
                        resource_id=resource_id,
                        exception=exception,
                    )
                )

        return tuple(failures)
