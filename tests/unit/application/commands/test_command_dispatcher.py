from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from earth_twin_engine.application.commands import (
    ApplicationCommand,
    CommandDispatcher,
)


@dataclass(frozen=True, slots=True)
class AddCommand(ApplicationCommand):
    first: int = 0
    second: int = 0


@dataclass(frozen=True, slots=True)
class MultiplyCommand(ApplicationCommand):
    first: int = 0
    second: int = 0


class AddHandler:
    def handle(self, command: AddCommand) -> int:
        return command.first + command.second


@pytest.fixture
def dispatcher() -> CommandDispatcher:
    return CommandDispatcher()


def test_register_handler(dispatcher: CommandDispatcher) -> None:
    dispatcher.register(AddCommand, AddHandler())

    assert dispatcher.is_registered(AddCommand)
    assert dispatcher.handler_count == 1


def test_dispatch_command(dispatcher: CommandDispatcher) -> None:
    dispatcher.register(AddCommand, AddHandler())

    command = AddCommand(first=12, second=8)
    result = dispatcher.dispatch(command)

    assert result.succeeded is True
    assert result.failed is False
    assert result.command is command
    assert result.value == 20
    assert result.failure is None


def test_dispatch_preserves_command_correlation_id(
    dispatcher: CommandDispatcher,
) -> None:
    from uuid import uuid4

    correlation_id = uuid4()
    dispatcher.register(AddCommand, AddHandler())

    command = AddCommand(
        first=2,
        second=3,
        correlation_id=correlation_id,
    )
    result = dispatcher.dispatch(command)

    assert result.command.correlation_id == correlation_id


def test_reject_duplicate_handler(
    dispatcher: CommandDispatcher,
) -> None:
    dispatcher.register(AddCommand, AddHandler())

    with pytest.raises(ValueError, match="already registered"):
        dispatcher.register(AddCommand, AddHandler())


def test_reject_invalid_command_type(
    dispatcher: CommandDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.register(str, AddHandler())  # type: ignore[arg-type]


def test_reject_invalid_handler(
    dispatcher: CommandDispatcher,
) -> None:
    with pytest.raises(TypeError, match="handle method"):
        dispatcher.register(AddCommand, object())  # type: ignore[arg-type]


def test_dispatch_unregistered_command(
    dispatcher: CommandDispatcher,
) -> None:
    command = AddCommand(first=1, second=2)

    result = dispatcher.dispatch(command)

    assert result.failed is True
    assert result.succeeded is False
    assert result.failure is not None
    assert isinstance(result.failure.exception, LookupError)
    assert result.failure.command_id == command.command_id


def test_dispatch_captures_handler_exception(
    dispatcher: CommandDispatcher,
) -> None:
    handler = Mock()
    handler.handle.side_effect = RuntimeError("Handler failed")
    dispatcher.register(AddCommand, handler)

    command = AddCommand(first=1, second=2)
    result = dispatcher.dispatch(command)

    assert result.failed is True
    assert result.failure is not None
    assert isinstance(result.failure.exception, RuntimeError)
    assert str(result.failure.exception) == "Handler failed"


def test_handler_failure_does_not_unregister_handler(
    dispatcher: CommandDispatcher,
) -> None:
    handler = Mock()
    handler.handle.side_effect = RuntimeError("Temporary failure")
    dispatcher.register(AddCommand, handler)

    result = dispatcher.dispatch(AddCommand())

    assert result.failed is True
    assert dispatcher.is_registered(AddCommand)


def test_unregister_handler(
    dispatcher: CommandDispatcher,
) -> None:
    dispatcher.register(AddCommand, AddHandler())

    assert dispatcher.unregister(AddCommand) is True
    assert dispatcher.is_registered(AddCommand) is False
    assert dispatcher.handler_count == 0


def test_unregister_missing_handler(
    dispatcher: CommandDispatcher,
) -> None:
    assert dispatcher.unregister(AddCommand) is False


def test_reject_invalid_unregister_type(
    dispatcher: CommandDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.unregister(str)  # type: ignore[arg-type]


def test_reject_invalid_registration_check(
    dispatcher: CommandDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.is_registered(str)  # type: ignore[arg-type]


def test_dispatch_requires_application_command(
    dispatcher: CommandDispatcher,
) -> None:
    with pytest.raises(TypeError):
        dispatcher.dispatch("invalid")  # type: ignore[arg-type]


def test_handler_for_one_command_type_does_not_handle_another(
    dispatcher: CommandDispatcher,
) -> None:
    dispatcher.register(AddCommand, AddHandler())

    result = dispatcher.dispatch(MultiplyCommand(first=3, second=4))

    assert result.failed is True
    assert result.failure is not None
    assert isinstance(result.failure.exception, LookupError)


def test_handler_returning_none_is_successful(
    dispatcher: CommandDispatcher,
) -> None:
    handler = Mock()
    handler.handle.return_value = None
    dispatcher.register(AddCommand, handler)

    result = dispatcher.dispatch(AddCommand())

    assert result.succeeded is True
    assert result.value is None
