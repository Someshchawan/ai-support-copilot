"""Runnable demo: shows the observability layer measuring quality, retrying
failures, and producing aggregate metrics — using a flaky mock model so it
runs with no API key.

    python demo.py
"""
from __future__ import annotations

import json
import random

from observability import ObservabilityMonitor, ResponseEvaluator, RetryPolicy


class FlakyModel:
    """A mock model that sometimes errors or returns a poor answer, so we can
    see failure detection and retries in action. Deterministic via seed."""

    GOOD = {
        "How do I reset my password?":
            "1. Go to the login page. 2. Click 'Forgot Password'. "
            "3. Enter your email. 4. Follow the reset link we send you.",
        "How do I create an API key?":
            "1. Open Settings. 2. Select 'API Keys'. 3. Click 'Create key' "
            "and copy the value. Store it securely; it is shown only once.",
    }

    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)

    def __call__(self, query: str) -> str:
        roll = self.rng.random()
        if roll < 0.25:
            raise TimeoutError("upstream API timed out")
        if roll < 0.55:
            return "I'm not sure."                       # fallback -> fails eval
        return self.GOOD.get(query, "Here are the steps you asked about.")


def main() -> None:
    model = FlakyModel(seed=7)
    monitor = ObservabilityMonitor(
        model,
        evaluator=ResponseEvaluator(threshold=0.6),
        policy=RetryPolicy(max_retries=3, base_delay=0.0),
    )

    queries = [
        "How do I reset my password?",
        "How do I create an API key?",
        "How do I reset my password?",
        "How do I create an API key?",
    ]
    print("=== Responses (with automatic retries on failure) ===\n")
    for q in queries:
        answer = monitor.handle(q)
        print(f"Q: {q}\nA: {answer}\n")

    print("=== Aggregate quality metrics ===")
    print(json.dumps(monitor.report(), indent=2))


if __name__ == "__main__":
    main()
