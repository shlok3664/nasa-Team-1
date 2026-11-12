"""Tests for the Earth Twin Engine package."""

from earth_twin_engine import __version__


def test_package_has_valid_version() -> None:
    assert __version__ == "0.1.0"
