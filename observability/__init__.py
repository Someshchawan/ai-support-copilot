"""Evaluation & observability layer for AI Support Copilot.

Measures response quality, detects failures, triggers retries, and produces
aggregate quality metrics.
"""
from .evaluator import ResponseEvaluator, EvaluationResult
from .reliability import RetryPolicy, call_with_retries, CallOutcome
from .metrics import MetricsAggregator, ResponseRecord
from .monitor import ObservabilityMonitor

__version__ = "0.1.0"
__all__ = [
    "ResponseEvaluator", "EvaluationResult",
    "RetryPolicy", "call_with_retries", "CallOutcome",
    "MetricsAggregator", "ResponseRecord",
    "ObservabilityMonitor",
]
