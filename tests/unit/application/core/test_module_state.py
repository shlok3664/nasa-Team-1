"""Tests for application module lifecycle states."""

from earth_twin_engine.application.core import ModuleState


def test_module_state_contains_all_lifecycle_states() -> None:
    assert {state.value for state in ModuleState} == {
        "registered",
        "initialized",
        "running",
        "stopped",
        "shutdown",
        "failed",
    }


def test_module_state_is_string_enum() -> None:
    assert ModuleState.RUNNING == "running"
    assert isinstance(ModuleState.RUNNING, str)
