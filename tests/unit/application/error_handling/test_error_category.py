from earth_twin_engine.application.error_handling import ErrorCategory


def test_error_categories_exist() -> None:
    assert ErrorCategory.CONFIGURATION.value == "configuration"
    assert ErrorCategory.LIFECYCLE.value == "lifecycle"
    assert ErrorCategory.VALIDATION.value == "validation"
    assert ErrorCategory.DATA.value == "data"
    assert ErrorCategory.NETWORK.value == "network"
    assert ErrorCategory.RESOURCE.value == "resource"
    assert ErrorCategory.INTERNAL.value == "internal"
    assert ErrorCategory.UNKNOWN.value == "unknown"
