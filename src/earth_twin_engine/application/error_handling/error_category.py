"""Categories used to classify application errors."""

from enum import Enum


class ErrorCategory(Enum):
    """Identifies the subsystem or nature of an application error."""

    CONFIGURATION = "configuration"
    LIFECYCLE = "lifecycle"
    VALIDATION = "validation"
    DATA = "data"
    NETWORK = "network"
    RESOURCE = "resource"
    INTERNAL = "internal"
    UNKNOWN = "unknown"
