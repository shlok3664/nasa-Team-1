"""Domain models for scientific interpretation results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ScientificInterpretation:
    """Verifiable explanation of a scientific result."""

    variable_id: str
    summary: str
    observed_pattern: str
    trend_magnitude: str
    statistical_evidence: str
    regional_comparison: str = ""
    confidence_and_uncertainty: str = ""
    data_limitations: str = ""
    methodological_notes: str = ""
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "variable_id",
            "summary",
            "observed_pattern",
            "trend_magnitude",
            "statistical_evidence",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict")
