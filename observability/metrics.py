"""Quality metrics: per-response records and aggregate reporting.

This module *produces quality metrics* — the aggregated view of how the
assistant is performing across many responses (pass rate, mean quality,
failure rate, retry rate, latency percentiles).
"""
from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class ResponseRecord:
    """A single evaluated response and how it was produced."""
    query: str
    passed: bool
    quality_score: float          # 0.0 - 1.0
    attempts: int                 # includes the successful/final attempt
    retried: bool
    failed: bool                  # True if no attempt met the quality bar
    latency_ms: float
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class MetricsAggregator:
    """Collects ResponseRecords and computes aggregate quality metrics."""

    def __init__(self) -> None:
        self._records: List[ResponseRecord] = []

    def record(self, r: ResponseRecord) -> None:
        self._records.append(r)

    @property
    def total(self) -> int:
        return len(self._records)

    def _pct(self, values: List[float], p: float) -> Optional[float]:
        if not values:
            return None
        values = sorted(values)
        k = (len(values) - 1) * p
        lo, hi = int(k), min(int(k) + 1, len(values) - 1)
        if lo == hi:
            return round(values[lo], 2)
        return round(values[lo] + (values[hi] - values[lo]) * (k - lo), 2)

    def summary(self) -> dict:
        n = self.total
        if n == 0:
            return {"total": 0}
        scores = [r.quality_score for r in self._records]
        latencies = [r.latency_ms for r in self._records]
        passed = sum(r.passed for r in self._records)
        failed = sum(r.failed for r in self._records)
        retried = sum(r.retried for r in self._records)
        total_attempts = sum(r.attempts for r in self._records)
        return {
            "total": n,
            "pass_rate": round(passed / n, 3),
            "failure_rate": round(failed / n, 3),
            "retry_rate": round(retried / n, 3),
            "avg_quality_score": round(statistics.mean(scores), 3),
            "min_quality_score": round(min(scores), 3),
            "avg_attempts": round(total_attempts / n, 2),
            "latency_ms_p50": self._pct(latencies, 0.50),
            "latency_ms_p95": self._pct(latencies, 0.95),
        }

    def to_json(self) -> str:
        return json.dumps({
            "summary": self.summary(),
            "records": [r.to_dict() for r in self._records],
        }, indent=2)

    def reset(self) -> None:
        self._records.clear()
