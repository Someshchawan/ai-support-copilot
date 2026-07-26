# Evaluation & Observability Layer

An evaluation and observability layer for **AI Support Copilot** that **measures
response quality, detects failures, triggers retries, and produces quality
metrics**. It turns "call the API and hope" into a monitored loop where AI output
is measured, not assumed correct.

Runs fully offline and deterministically (no API key needed) so it can be tested
in CI.

## What it does

| Capability | Where | How |
|---|---|---|
| **Measures response quality** | `evaluator.py` | Scores each response 0–1 across relevance, length adequacy, structure/actionability, and hedging — returns a pass/fail against a configurable threshold. |
| **Detects failures** | `evaluator.py` | Hard-fails empty output, error markers, and fallback/non-answer responses ("I don't know", "I'm not sure"). |
| **Triggers retries** | `reliability.py` | `call_with_retries` re-invokes the model on exceptions *and* on low-quality responses, with exponential backoff, and keeps the best attempt. |
| **Produces quality metrics** | `metrics.py` | Aggregates pass rate, failure rate, retry rate, mean/min quality score, average attempts, and latency p50/p95 across all responses. |
| **Ties it together** | `monitor.py` | `ObservabilityMonitor` runs the full loop per query and exposes `.report()` for aggregate metrics. |

## Quick start

```python
from observability import ObservabilityMonitor, ResponseEvaluator, RetryPolicy

def model(query: str) -> str:
    ...  # your existing src/copilot.py call

monitor = ObservabilityMonitor(
    model,
    evaluator=ResponseEvaluator(threshold=0.6),
    policy=RetryPolicy(max_retries=3),
)

answer = monitor.handle("How do I reset my password?")
print(monitor.report())
# {'total': 1, 'pass_rate': 1.0, 'failure_rate': 0.0, 'retry_rate': 0.0,
#  'avg_quality_score': 0.86, 'avg_attempts': 1.0, 'latency_ms_p50': ...}
```

Run the end-to-end demo with a flaky mock model (shows retries and metrics):

```bash
python demo.py
```

## How it fits the flow

```
[User query]
     ↓
[src/copilot.py  ── your model call]
     ↓
call_with_retries ──► ResponseEvaluator (measure quality / detect failure)
     │   ▲                     │
     │   └── retry on fail ────┘
     ↓
ObservabilityMonitor ──► MetricsAggregator (produce quality metrics)
     ↓
[Best response + report()]
```

## Tests

```bash
pip install pytest
python -m pytest tests/test_observability.py -v          # 11 passing tests
```

## Layout

```
observability/
├── evaluator.py      # measures quality, detects failures
├── reliability.py    # retry policy + call_with_retries
├── metrics.py        # ResponseRecord + MetricsAggregator (quality metrics)
└── monitor.py        # ObservabilityMonitor: end-to-end loop + report()
demo.py               # runnable demo with a flaky mock model
tests/test_observability.py                # 11 passing tests (at repo root)
```

## Wiring it to the existing copilot

Pass your real model call (from `src/copilot.py`) as the `model` callable to
`ObservabilityMonitor`. The layer wraps it without changing your prompt or API
logic — it observes, evaluates, and retries around it.
