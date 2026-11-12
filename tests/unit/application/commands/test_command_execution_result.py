from uuid import uuid4

import pytest

from earth_twin_engine.application.commands import (
    ApplicationCommand,
    CommandDispatchFailure,
    CommandExecutionResult,
)


def test_successful_execution_result() -> None:
    command = ApplicationCommand()
    result = CommandExecutionResult(command=command, value=42)

    assert result.succeeded is True
    assert result.failed is False
    assert result.value == 42
    assert result.failure is None


def test_failed_execution_result() -> None:
    command = ApplicationCommand()
    failure = CommandDispatchFailure(
        command_id=command.command_id,
        command_type="ApplicationCommand",
        exception=RuntimeError("Execution failed"),
    )
    result = CommandExecutionResult(
        command=command,
        failure=failure,
    )

    assert result.failed is True
    assert result.succeeded is False
    assert result.failure is failure


def test_reject_invalid_command() -> None:
    with pytest.raises(TypeError):
        CommandExecutionResult(command="invalid")  # type: ignore[arg-type]


def test_reject_invalid_failure() -> None:
    with pytest.raises(TypeError):
        CommandExecutionResult(
            command=ApplicationCommand(),
            failure="invalid",  # type: ignore[arg-type]
        )


def test_reject_failure_for_different_command() -> None:
    command = ApplicationCommand()
    failure = CommandDispatchFailure(
        command_id=uuid4(),
        command_type="ApplicationCommand",
        exception=RuntimeError("Execution failed"),
    )

    with pytest.raises(ValueError, match="must match"):
        CommandExecutionResult(
            command=command,
            failure=failure,
        )


def test_reject_invalid_failure_command_id() -> None:
    with pytest.raises(TypeError):
        CommandDispatchFailure(
            command_id="invalid",  # type: ignore[arg-type]
            command_type="ApplicationCommand",
            exception=RuntimeError("Execution failed"),
        )


def test_reject_empty_failure_command_type() -> None:
    with pytest.raises(ValueError):
        CommandDispatchFailure(
            command_id=uuid4(),
            command_type=" ",
            exception=RuntimeError("Execution failed"),
        )


def test_reject_invalid_failure_exception() -> None:
    with pytest.raises(TypeError):
        CommandDispatchFailure(
            command_id=uuid4(),
            command_type="ApplicationCommand",
            exception="invalid",  # type: ignore[arg-type]
        )
