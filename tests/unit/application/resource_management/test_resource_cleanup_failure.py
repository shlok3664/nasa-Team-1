import pytest

from earth_twin_engine.application.resource_management import (
    ResourceCleanupFailure,
)


def test_create_cleanup_failure() -> None:
    exception = RuntimeError("Cleanup failed")

    failure = ResourceCleanupFailure(
        resource_id="dataset_reader",
        exception=exception,
    )

    assert failure.resource_id == "dataset_reader"
    assert failure.exception is exception


@pytest.mark.parametrize("resource_id", ["", " "])
def test_reject_invalid_resource_id(resource_id: str) -> None:
    with pytest.raises(ValueError):
        ResourceCleanupFailure(
            resource_id=resource_id,
            exception=RuntimeError("Cleanup failed"),
        )


def test_reject_invalid_exception() -> None:
    with pytest.raises(TypeError):
        ResourceCleanupFailure(
            resource_id="dataset_reader",
            exception="not an exception",  # type: ignore[arg-type]
        )
