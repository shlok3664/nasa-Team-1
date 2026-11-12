import pytest

from earth_twin_engine.application.modules.region_manager.region_manager import (
    RegionManager,
)
from earth_twin_engine.application.modules.region_manager.region_manager_errors import (
    DuplicateRegionError,
    RegionNotFoundError,
)
from earth_twin_engine.domain.geography import SpatialCoordinate


def test_register_region(
    india_region,
) -> None:
    manager = RegionManager()

    manager.register(india_region)

    assert manager.region_count == 1
    assert manager.get_region("india") == india_region


def test_reject_duplicate_region(
    india_region,
) -> None:
    manager = RegionManager()
    manager.register(india_region)

    with pytest.raises(DuplicateRegionError):
        manager.register(india_region)


def test_reject_invalid_region() -> None:
    manager = RegionManager()

    with pytest.raises(TypeError):
        manager.register(None)


def test_unregister_region(
    india_region,
) -> None:
    manager = RegionManager()
    manager.register(india_region)

    assert manager.unregister("india") is True
    assert manager.region_count == 0


def test_unregister_missing_region() -> None:
    manager = RegionManager()

    assert manager.unregister("india") is False


def test_get_missing_region() -> None:
    manager = RegionManager()

    with pytest.raises(RegionNotFoundError):
        manager.get_region("india")


def test_all_regions_are_sorted(
    india_region,
    japan_region,
    maharashtra_region,
) -> None:
    manager = RegionManager()
    manager.register(japan_region)
    manager.register(india_region)
    manager.register(maharashtra_region)

    regions = manager.all_regions()

    assert [region.region_id for region in regions] == [
        "india",
        "japan",
        "maharashtra",
    ]


def test_find_regions_containing_coordinate(
    india_region,
    maharashtra_region,
    japan_region,
    nagpur_coordinate,
) -> None:
    manager = RegionManager()

    manager.register(india_region)
    manager.register(maharashtra_region)
    manager.register(japan_region)

    regions = manager.find_containing(nagpur_coordinate)

    assert [region.region_id for region in regions] == [
        "india",
        "maharashtra",
    ]


def test_find_regions_returns_empty_when_no_match(
    india_region,
    japan_region,
) -> None:
    manager = RegionManager()
    manager.register(india_region)
    manager.register(japan_region)

    regions = manager.find_containing(SpatialCoordinate(latitude=35.6762, longitude=139.6503))

    assert [region.region_id for region in regions] == ["japan"]


def test_find_containing_rejects_invalid_coordinate(
    india_region,
) -> None:
    manager = RegionManager()
    manager.register(india_region)

    with pytest.raises(TypeError):
        manager.find_containing(None)


def test_reject_invalid_region_id(
    india_region,
) -> None:
    manager = RegionManager()

    with pytest.raises(TypeError):
        manager.get_region(None)


def test_reject_blank_region_id() -> None:
    manager = RegionManager()

    with pytest.raises(ValueError):
        manager.get_region(" ")
