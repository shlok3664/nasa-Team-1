from unittest.mock import Mock

import pytest

from earth_twin_engine.application.resource_management import (
    ResourceCleanupFailure,
    ResourceManager,
)


@pytest.fixture
def manager() -> ResourceManager:
    return ResourceManager()


def test_initial_state(manager: ResourceManager) -> None:
    assert manager.resource_count == 0
    assert manager.is_shutdown is False


def test_register_and_resolve_resource(manager: ResourceManager) -> None:
    resource = object()
    cleanup = Mock()

    manager.register("dataset_reader", resource, cleanup)

    assert manager.resolve("dataset_reader") is resource
    assert manager.get("dataset_reader") is resource
    assert manager.resource_count == 1


def test_get_missing_resource_returns_none(manager: ResourceManager) -> None:
    assert manager.get("missing") is None


def test_resolve_missing_resource_raises(manager: ResourceManager) -> None:
    with pytest.raises(KeyError, match="Resource is not registered"):
        manager.resolve("missing")


def test_reject_duplicate_resource_id(manager: ResourceManager) -> None:
    manager.register("reader", object(), Mock())

    with pytest.raises(ValueError, match="already registered"):
        manager.register("reader", object(), Mock())


@pytest.mark.parametrize("resource_id", ["", " "])
def test_reject_invalid_resource_id(
    manager: ResourceManager,
    resource_id: str,
) -> None:
    with pytest.raises(ValueError):
        manager.register(resource_id, object(), Mock())


def test_reject_none_resource(manager: ResourceManager) -> None:
    with pytest.raises(ValueError):
        manager.register("reader", None, Mock())


def test_reject_non_callable_cleanup(manager: ResourceManager) -> None:
    with pytest.raises(TypeError):
        manager.register(
            "reader",
            object(),
            None,  # type: ignore[arg-type]
        )


def test_release_resource(manager: ResourceManager) -> None:
    resource = object()
    cleanup = Mock()

    manager.register("reader", resource, cleanup)

    result = manager.release("reader")

    assert result is None
    cleanup.assert_called_once_with(resource)
    assert manager.get("reader") is None
    assert manager.resource_count == 0


def test_release_missing_resource_raises(manager: ResourceManager) -> None:
    with pytest.raises(KeyError):
        manager.release("missing")


def test_release_returns_cleanup_failure(manager: ResourceManager) -> None:
    resource = object()
    exception = RuntimeError("Unable to close resource")

    def cleanup(_: object) -> None:
        raise exception

    manager.register("reader", resource, cleanup)

    failure = manager.release("reader")

    assert isinstance(failure, ResourceCleanupFailure)
    assert failure.resource_id == "reader"
    assert failure.exception is exception
    assert manager.get("reader") is None


def test_shutdown_cleans_up_resources_in_reverse_order(
    manager: ResourceManager,
) -> None:
    cleanup_order: list[str] = []

    manager.register(
        "first",
        object(),
        lambda _: cleanup_order.append("first"),
    )
    manager.register(
        "second",
        object(),
        lambda _: cleanup_order.append("second"),
    )
    manager.register(
        "third",
        object(),
        lambda _: cleanup_order.append("third"),
    )

    failures = manager.shutdown()

    assert failures == ()
    assert cleanup_order == ["third", "second", "first"]
    assert manager.resource_count == 0
    assert manager.is_shutdown is True


def test_shutdown_continues_after_cleanup_failure(
    manager: ResourceManager,
) -> None:
    cleanup_order: list[str] = []

    def failing_cleanup(_: object) -> None:
        cleanup_order.append("failing")
        raise RuntimeError("Cleanup failed")

    manager.register(
        "first",
        object(),
        lambda _: cleanup_order.append("first"),
    )
    manager.register("failing", object(), failing_cleanup)
    manager.register(
        "last",
        object(),
        lambda _: cleanup_order.append("last"),
    )

    failures = manager.shutdown()

    assert cleanup_order == ["last", "failing", "first"]
    assert len(failures) == 1
    assert failures[0].resource_id == "failing"
    assert isinstance(failures[0].exception, RuntimeError)


def test_shutdown_is_idempotent(manager: ResourceManager) -> None:
    cleanup = Mock()
    manager.register("reader", object(), cleanup)

    first_result = manager.shutdown()
    second_result = manager.shutdown()

    assert first_result == ()
    assert second_result == ()
    cleanup.assert_called_once()


def test_cannot_register_after_shutdown(manager: ResourceManager) -> None:
    manager.shutdown()

    with pytest.raises(RuntimeError, match="after shutdown"):
        manager.register("reader", object(), Mock())


def test_cannot_release_after_shutdown(manager: ResourceManager) -> None:
    manager.register("reader", object(), Mock())
    manager.shutdown()

    with pytest.raises(RuntimeError, match="after shutdown"):
        manager.release("reader")


def test_shutdown_empty_manager(manager: ResourceManager) -> None:
    failures = manager.shutdown()

    assert failures == ()
    assert manager.is_shutdown is True
    assert manager.resource_count == 0


def test_released_resource_is_not_cleaned_up_again(
    manager: ResourceManager,
) -> None:
    cleanup = Mock()
    manager.register("reader", object(), cleanup)

    manager.release("reader")
    manager.shutdown()

    cleanup.assert_called_once()
