"""Lifecycle states for application modules."""

from enum import StrEnum


class ModuleState(StrEnum):
    """Represents the lifecycle state of an application module."""

    REGISTERED = "registered"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    SHUTDOWN = "shutdown"
    FAILED = "failed"
