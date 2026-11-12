"""Contextual information associated with an application error."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ErrorContext:
    """Provides contextual information for error diagnosis."""

    correlation_id: UUID | None = None
    module_id: str | None = None
    operation: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.correlation_id is not None and not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID or None")

        if self.module_id is not None:
            if not isinstance(self.module_id, str) or not self.module_id.strip():
                raise ValueError("module_id must be a non-empty string or None")

        if self.operation is not None:
            if not isinstance(self.operation, str) or not self.operation.strip():
                raise ValueError("operation must be a non-empty string or None")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        metadata = dict(self.metadata)

        if any(not isinstance(key, str) or not key.strip() for key in metadata):
            raise ValueError("metadata keys must be non-empty strings")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(metadata),
        )
