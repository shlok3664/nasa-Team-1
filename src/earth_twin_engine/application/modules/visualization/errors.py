"""Errors raised by the visualization module."""


class VisualizationError(Exception):
    """Base exception for visualization errors."""


class VisualizationDataError(VisualizationError):
    """Raised when visualization-ready data cannot be constructed."""

