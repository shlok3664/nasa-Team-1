from earth_twin_engine.application.logging import LogLevel


def test_log_level_values() -> None:
    assert LogLevel.DEBUG == 10
    assert LogLevel.INFO == 20
    assert LogLevel.WARNING == 30
    assert LogLevel.ERROR == 40
    assert LogLevel.CRITICAL == 50


def test_log_levels_are_ordered() -> None:
    assert LogLevel.DEBUG < LogLevel.INFO
    assert LogLevel.INFO < LogLevel.WARNING
    assert LogLevel.WARNING < LogLevel.ERROR
    assert LogLevel.ERROR < LogLevel.CRITICAL
