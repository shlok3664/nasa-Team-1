from uuid import uuid4

import pytest

from earth_twin_engine.application.error_handling import ErrorContext


def test_create_error_context() -> None:
    correlation_id = uuid4()

    context = ErrorContext(
        correlation_id=correlation_id,
        module_id="data_acquisition",
        operation="retrieve_dataset",
        metadata={"source": "NASA", "attempt": 2},
    )

    assert context.correlation_id == correlation_id
    assert context.module_id == "data_acquisition"
    assert context.operation == "retrieve_dataset"
    assert context.metadata["source"] == "NASA"
    assert context.metadata["attempt"] == 2


def test_default_context() -> None:
    context = ErrorContext()

    assert context.correlation_id is None
    assert context.module_id is None
    assert context.operation is None
    assert context.metadata == {}


def test_optional_fields_accept_none() -> None:
    context = ErrorContext(
        correlation_id=None,
        module_id=None,
        operation=None,
    )

    assert context.correlation_id is None
    assert context.module_id is None
    assert context.operation is None


def test_metadata_is_immutable() -> None:
    original = {"source": "NASA"}
    context = ErrorContext(metadata=original)

    original["source"] = "Other"

    assert context.metadata["source"] == "NASA"

    with pytest.raises(TypeError):
        context.metadata["source"] = "Other"  # type: ignore[index]


@pytest.mark.parametrize("value", ["", " ", 123])
def test_reject_invalid_module_id(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        ErrorContext(module_id=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", " ", 123])
def test_reject_invalid_operation(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        ErrorContext(operation=value)  # type: ignore[arg-type]


def test_reject_invalid_correlation_id() -> None:
    with pytest.raises(TypeError):
        ErrorContext(correlation_id="not-a-uuid")  # type: ignore[arg-type]


def test_reject_invalid_metadata() -> None:
    with pytest.raises(TypeError):
        ErrorContext(metadata=["invalid"])  # type: ignore[arg-type]


def test_reject_empty_metadata_key() -> None:
    with pytest.raises(ValueError):
        ErrorContext(metadata={" ": "value"})
