"""Lifecycle states of the application runtime."""

from enum import Enum


class RuntimeState(Enum):
    """Represents the current application runtime state."""

    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    SHUTDOWN = "shutdown"
