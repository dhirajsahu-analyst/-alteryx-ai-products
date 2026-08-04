"""Metrics Engine - Core metric resolution and query execution"""

__version__ = "1.0.0"

from engine.metric_engine import MetricsEngine
from engine.error_handler import MetricError, MetricNotFoundError, CompositionError

__all__ = [
    "MetricsEngine",
    "MetricError",
    "MetricNotFoundError",
    "CompositionError",
]
