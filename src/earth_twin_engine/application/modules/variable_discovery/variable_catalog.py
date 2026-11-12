"""Thread-safe catalog of discoverable Earth science variables."""

from threading import RLock

from earth_twin_engine.domain.temporal.temporal_resolution import (
    TemporalResolution,
)
from earth_twin_engine.domain.variables.earth_variable import EarthVariable
from earth_twin_engine.domain.variables.variable_category import VariableCategory


class VariableCatalog:
    """Stores and searches registered Earth science variable definitions."""

    def __init__(self, variables: tuple[EarthVariable, ...] = ()) -> None:
        self._variables: dict[str, EarthVariable] = {}
        self._lock = RLock()

        if not isinstance(variables, tuple):
            raise TypeError("variables must be a tuple")

        for variable in variables:
            self.register(variable)

    def register(self, variable: EarthVariable) -> None:
        """Register a variable, rejecting duplicate identifiers."""

        if not isinstance(variable, EarthVariable):
            raise TypeError("variable must be an EarthVariable")

        with self._lock:
            if variable.variable_id in self._variables:
                raise ValueError(f"variable is already registered: {variable.variable_id}")

            self._variables[variable.variable_id] = variable

    def unregister(self, variable_id: str) -> bool:
        """Remove a variable by identifier."""

        self._validate_variable_id(variable_id)

        with self._lock:
            return self._variables.pop(variable_id, None) is not None

    def get(self, variable_id: str) -> EarthVariable:
        """Retrieve a variable or raise KeyError."""

        self._validate_variable_id(variable_id)

        with self._lock:
            variable = self._variables.get(variable_id)

        if variable is None:
            raise KeyError(f"Earth variable is not registered: {variable_id}")

        return variable

    def find(self, variable_id: str) -> EarthVariable | None:
        """Retrieve a variable without raising when it is absent."""

        self._validate_variable_id(variable_id)

        with self._lock:
            return self._variables.get(variable_id)

    def discover(
        self,
        category: VariableCategory | None = None,
        keyword: str | None = None,
        temporal_resolution: TemporalResolution | None = None,
        source_id: str | None = None,
    ) -> tuple[EarthVariable, ...]:
        """Find variables matching all supplied filters."""

        if category is not None and not isinstance(category, VariableCategory):
            raise TypeError("category must be a VariableCategory or None")

        if temporal_resolution is not None and not isinstance(
            temporal_resolution, TemporalResolution
        ):
            raise TypeError("temporal_resolution must be a TemporalResolution or None")

        if keyword is not None:
            if not isinstance(keyword, str):
                raise TypeError("keyword must be a string or None")
            if not keyword.strip():
                raise ValueError("keyword cannot be empty or whitespace")

        if source_id is not None:
            if not isinstance(source_id, str):
                raise TypeError("source_id must be a string or None")
            if not source_id.strip():
                raise ValueError("source_id cannot be empty or whitespace")

        normalized_keyword = keyword.casefold().strip() if keyword else None
        normalized_source = source_id.casefold().strip() if source_id else None

        with self._lock:
            variables = tuple(self._variables.values())

        matches = []

        for variable in variables:
            if category is not None and variable.category is not category:
                continue

            metadata = variable.metadata

            if temporal_resolution is not None:
                if temporal_resolution not in metadata.temporal_resolutions:
                    continue

            if normalized_source is not None:
                if not any(
                    source.casefold() == normalized_source for source in metadata.source_ids
                ):
                    continue

            if normalized_keyword is not None:
                searchable_text = " ".join(
                    (
                        variable.variable_id,
                        variable.name,
                        variable.description,
                        *metadata.keywords,
                    )
                ).casefold()

                if normalized_keyword not in searchable_text:
                    continue

            matches.append(variable)

        return tuple(sorted(matches, key=lambda item: item.variable_id))

    @property
    def variable_count(self) -> int:
        """Return the number of registered variables."""

        with self._lock:
            return len(self._variables)

    def all(self) -> tuple[EarthVariable, ...]:
        """Return all variables in deterministic identifier order."""

        with self._lock:
            return tuple(self._variables[key] for key in sorted(self._variables))

    @staticmethod
    def _validate_variable_id(variable_id: str) -> None:
        if not isinstance(variable_id, str):
            raise TypeError("variable_id must be a string")

        if not variable_id.strip():
            raise ValueError("variable_id cannot be empty or whitespace")
