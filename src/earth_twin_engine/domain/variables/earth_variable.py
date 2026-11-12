"""Earth science variable domain entity."""

import re
from dataclasses import dataclass

from earth_twin_engine.domain.variables.variable_category import (
    VariableCategory,
)
from earth_twin_engine.domain.variables.variable_metadata import (
    VariableMetadata,
)

_VARIABLE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class EarthVariable:
    """Represents a discoverable Earth science variable."""

    variable_id: str
    name: str
    description: str
    category: VariableCategory
    metadata: VariableMetadata

    def __post_init__(self) -> None:
        if not isinstance(self.variable_id, str):
            raise TypeError("variable_id must be a string")

        if not _VARIABLE_ID_PATTERN.fullmatch(self.variable_id):
            raise ValueError(
                "variable_id must use lowercase letters, numbers, "
                "and underscores, starting with a letter"
            )

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")

        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")

        if not isinstance(self.category, VariableCategory):
            raise TypeError("category must be a VariableCategory")

        if not isinstance(self.metadata, VariableMetadata):
            raise TypeError("metadata must be a VariableMetadata")
