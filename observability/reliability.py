"""Reliability: *detects failures and triggers retries*.

Wraps a model call so that transient exceptions AND low-quality responses
trigger a bounded number of retries with exponential backoff. Returns the best
attempt seen along with a full attempt trace for observability.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .evaluator import ResponseEvaluator, EvaluationResult


@dataclass
class RetryPolicy:
    max_retries: int = 2               # retries *after* the first attempt
    base_delay: float = 0.0            # seconds; 0 keeps tests fast
    backoff: float = 2.0               # multiplier per retry


@dataclass
class Attempt:
    index: int
    response: Optional[str]
    evaluation: Optional[EvaluationResult]
    error: Optional[str] = None


@dataclass
class CallOutcome:
    response: Optional[str]
    evaluation: Optional[EvaluationResult]
    attempts: List[Attempt] = field(default_factory=list)
    latency_ms: float = 0.0

    @property
    def succeeded(self) -> bool:
        return bool(self.evaluation and self.evaluation.passed)

    @property
    def retried(self) -> bool:
        return len(self.attempts) > 1


def call_with_retries(
    model: Callable[[str], str],
    query: str,
    evaluator: ResponseEvaluator,
    policy: RetryPolicy | None = None,
) -> CallOutcome:
    """Call `model(query)`, evaluate the result, and retry on failure.

    A retry is triggered when the model raises OR when the response fails the
    evaluator's quality bar. The best (highest-scoring) attempt is returned.
    """
    policy = policy or RetryPolicy()
    attempts: List[Attempt] = []
    best: Optional[Attempt] = None
    start = time.perf_counter()

    for i in range(policy.max_retries + 1):
        try:
            response = model(query)
            evaluation = evaluator.evaluate(query, response)
            attempt = Attempt(i, response, evaluation)
        except Exception as e:  # noqa: BLE001 - we deliberately capture all
            attempt = Attempt(i, None, None, error=f"{type(e).__name__}: {e}")

        attempts.append(attempt)

        # Track the best attempt so far (passing > higher score > any).
        if best is None:
            best = attempt
        elif attempt.evaluation and (
            best.evaluation is None
            or attempt.evaluation.score > best.evaluation.score
        ):
            best = attempt

        if attempt.evaluation and attempt.evaluation.passed:
            break  # success — stop retrying

        # Back off before the next retry (skip after the last attempt).
        if i < policy.max_retries and policy.base_delay:
            time.sleep(policy.base_delay * (policy.backoff ** i))

    latency_ms = (time.perf_counter() - start) * 1000.0
    return CallOutcome(
        response=best.response if best else None,
        evaluation=best.evaluation if best else None,
        attempts=attempts,
        latency_ms=round(latency_ms, 2),
    )
