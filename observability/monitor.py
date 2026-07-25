"""ObservabilityMonitor: the single entry point that ties the layer together.

For each query it: calls the model with retries, measures response quality,
detects failures, and records a metric — then `.report()` produces aggregate
quality metrics across everything it has seen.
"""
from __future__ import annotations

from typing import Callable

from .evaluator import ResponseEvaluator
from .metrics import MetricsAggregator, ResponseRecord
from .reliability import RetryPolicy, call_with_retries


class ObservabilityMonitor:
    def __init__(
        self,
        model: Callable[[str], str],
        evaluator: ResponseEvaluator | None = None,
        policy: RetryPolicy | None = None,
    ) -> None:
        self.model = model
        self.evaluator = evaluator or ResponseEvaluator()
        self.policy = policy or RetryPolicy()
        self.metrics = MetricsAggregator()

    def handle(self, query: str) -> str:
        """Process one query end-to-end and record its quality metric."""
        outcome = call_with_retries(self.model, query, self.evaluator, self.policy)
        ev = outcome.evaluation
        record = ResponseRecord(
            query=query,
            passed=outcome.succeeded,
            quality_score=ev.score if ev else 0.0,
            attempts=len(outcome.attempts),
            retried=outcome.retried,
            failed=not outcome.succeeded,
            latency_ms=outcome.latency_ms,
            reasons=ev.reasons if ev else ["no successful attempt"],
        )
        self.metrics.record(record)
        return outcome.response or ""

    def report(self) -> dict:
        """Return aggregate quality metrics collected so far."""
        return self.metrics.summary()
