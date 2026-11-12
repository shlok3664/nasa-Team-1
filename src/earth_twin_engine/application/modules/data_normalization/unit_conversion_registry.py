"""Explicit and configurable scientific unit conversions."""

from math import isfinite
from threading import RLock

from .normalization_error import UnsupportedUnitConversionError


class UnitConversionRegistry:
    """Stores explicit conversions between scientific units."""

    def __init__(self, include_defaults: bool = True) -> None:
        if not isinstance(include_defaults, bool):
            raise TypeError("include_defaults must be a bool.")

        self._conversions: dict[tuple[str, str], tuple[float, float]] = {}
        self._lock = RLock()

        if include_defaults:
            self._register_default_conversions()

    @staticmethod
    def _normalize_unit(unit: str) -> str:
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError("unit must be a non-empty string.")

        return " ".join(unit.strip().lower().split())

    def register(
        self,
        source_unit: str,
        target_unit: str,
        factor: float,
        offset: float = 0.0,
        *,
        replace_existing: bool = False,
    ) -> None:
        """Register an explicit affine unit conversion."""

        source = self._normalize_unit(source_unit)
        target = self._normalize_unit(target_unit)

        if isinstance(factor, bool) or not isinstance(factor, (int, float)):
            raise TypeError("factor must be numeric.")

        if isinstance(offset, bool) or not isinstance(offset, (int, float)):
            raise TypeError("offset must be numeric.")

        if not isfinite(factor) or factor == 0:
            raise ValueError("factor must be finite and non-zero.")

        if not isfinite(offset):
            raise ValueError("offset must be finite.")

        if not isinstance(replace_existing, bool):
            raise TypeError("replace_existing must be a bool.")

        key = (source, target)

        with self._lock:
            if key in self._conversions and not replace_existing:
                raise ValueError(
                    f"Conversion from '{source_unit}' to '{target_unit}' is already registered."
                )

            self._conversions[key] = (float(factor), float(offset))

    def supports(self, source_unit: str, target_unit: str) -> bool:
        """Return whether a conversion is explicitly available."""

        source = self._normalize_unit(source_unit)
        target = self._normalize_unit(target_unit)

        if source == target:
            return True

        with self._lock:
            return (source, target) in self._conversions

    def convert(
        self,
        value: float,
        source_unit: str,
        target_unit: str,
    ) -> float:
        """Convert a finite numeric value into the requested unit."""

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("value must be numeric.")

        if not isfinite(value):
            raise ValueError("value must be finite.")

        source = self._normalize_unit(source_unit)
        target = self._normalize_unit(target_unit)

        if source == target:
            return float(value)

        with self._lock:
            conversion = self._conversions.get((source, target))

        if conversion is None:
            raise UnsupportedUnitConversionError(
                f"No conversion is registered from '{source_unit}' to '{target_unit}'."
            )

        factor, offset = conversion
        result = float(value) * factor + offset

        if not isfinite(result):
            raise ValueError("Unit conversion produced a non-finite result.")

        return result

    def _register_default_conversions(self) -> None:
        """Register commonly used scientific conversions."""

        conversions = (
            ("c", "k", 1.0, 273.15),
            ("°c", "k", 1.0, 273.15),
            ("celsius", "k", 1.0, 273.15),
            ("k", "c", 1.0, -273.15),
            ("k", "°c", 1.0, -273.15),
            ("k", "celsius", 1.0, -273.15),
            ("f", "k", 5.0 / 9.0, 255.3722222222222),
            ("°f", "k", 5.0 / 9.0, 255.3722222222222),
            ("km/h", "m/s", 1.0 / 3.6, 0.0),
            ("m/s", "km/h", 3.6, 0.0),
            ("pa", "hpa", 0.01, 0.0),
            ("hpa", "pa", 100.0, 0.0),
            ("pa", "kpa", 0.001, 0.0),
            ("kpa", "pa", 1000.0, 0.0),
            ("mm", "m", 0.001, 0.0),
            ("m", "mm", 1000.0, 0.0),
            ("percent", "fraction", 0.01, 0.0),
            ("%", "fraction", 0.01, 0.0),
            ("fraction", "percent", 100.0, 0.0),
            ("fraction", "%", 100.0, 0.0),
        )

        for source, target, factor, offset in conversions:
            self.register(source, target, factor, offset)
