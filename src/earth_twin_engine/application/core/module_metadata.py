"""Metadata contracts for application modules."""

import re
from dataclasses import dataclass

_MODULE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class ModuleMetadata:
    """Describes an application module and its dependencies."""

    module_id: str
    name: str
    version: str
    dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.module_id, str):
            raise TypeError("module_id must be a string")

        if not _MODULE_ID_PATTERN.fullmatch(self.module_id):
            raise ValueError(
                "module_id must start with a lowercase letter and contain "
                "only lowercase letters, numbers, and underscores"
            )

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")

        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version must be a non-empty string")

        if not isinstance(self.dependencies, tuple):
            raise TypeError("dependencies must be a tuple")

        for dependency in self.dependencies:
            if not isinstance(dependency, str):
                raise TypeError("dependencies must contain strings")

            if not _MODULE_ID_PATTERN.fullmatch(dependency):
                raise ValueError("dependency contains an invalid module ID")

            if dependency == self.module_id:
                raise ValueError("a module cannot depend on itself")

        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("dependencies cannot contain duplicates")
