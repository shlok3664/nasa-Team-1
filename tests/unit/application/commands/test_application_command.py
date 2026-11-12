from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from earth_twin_engine.application.commands import ApplicationCommand


def test_create_command() -> None:
    command = ApplicationCommand()

    assert isinstance(command.command_id, UUID)
    assert command.issued_at.tzinfo is UTC
    assert command.correlation_id is None


def test_create_command_with_correlation_id() -> None:
    correlation_id = uuid4()
    command = ApplicationCommand(correlation_id=correlation_id)

    assert command.correlation_id == correlation_id


def test_command_ids_are_unique() -> None:
    first = ApplicationCommand()
    second = ApplicationCommand()

    assert first.command_id != second.command_id


def test_reject_invalid_command_id() -> None:
    with pytest.raises(TypeError):
        ApplicationCommand(command_id="invalid")  # type: ignore[arg-type]


def test_reject_naive_issued_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ApplicationCommand(
            issued_at=datetime(2026, 1, 1),  # type: ignore[arg-type]
        )


def test_reject_invalid_issued_at_type() -> None:
    with pytest.raises(TypeError):
        ApplicationCommand(issued_at="invalid")  # type: ignore[arg-type]


def test_reject_invalid_correlation_id() -> None:
    with pytest.raises(TypeError):
        ApplicationCommand(correlation_id="invalid")  # type: ignore[arg-type]


def test_command_is_immutable() -> None:
    command = ApplicationCommand()

    with pytest.raises(AttributeError):
        command.command_id = uuid4()  # type: ignore[misc]
