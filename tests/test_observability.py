"""Tests for the evaluation & observability layer."""
import pytest

from observability import (
    ResponseEvaluator, RetryPolicy, call_with_retries,
    MetricsAggregator, ResponseRecord, ObservabilityMonitor,
)


# ---------- evaluator: measures quality + detects failures ----------

def test_good_response_passes():
    ev = ResponseEvaluator()
    r = ev.evaluate(
        "How do I reset my password?",
        "1. Open the login page. 2. Click 'Forgot Password'. "
        "3. Enter your email and follow the reset link.",
    )
    assert r.passed
    assert r.score >= 0.6
    assert not r.failure


def test_empty_response_is_hard_failure():
    ev = ResponseEvaluator()
    r = ev.evaluate("How do I reset my password?", "")
    assert not r.passed and r.failure and r.score == 0.0


def test_fallback_response_detected():
    ev = ResponseEvaluator()
    r = ev.evaluate("How do I reset my password?", "I'm not sure.")
    assert not r.passed and r.failure


def test_error_marker_detected():
    ev = ResponseEvaluator()
    r = ev.evaluate("Question?", "<error> traceback ...")
    assert not r.passed and r.failure


def test_irrelevant_response_scores_low():
    ev = ResponseEvaluator()
    good = ev.evaluate("How do I create an API key?",
                       "Open Settings, choose API Keys, click Create key.")
    bad = ev.evaluate("How do I create an API key?",
                      "The weather is nice and sunny today outside.")
    assert good.score > bad.score


# ---------- reliability: triggers retries ----------

def test_retries_until_success():
    calls = {"n": 0}

    def flaky(_q):
        calls["n"] += 1
        if calls["n"] < 3:
            return "I don't know."           # fails eval -> retry
        return "1. Open Settings. 2. Click API Keys. 3. Create a key."

    ev = ResponseEvaluator()
    outcome = call_with_retries(flaky, "How do I create an API key?", ev,
                                RetryPolicy(max_retries=3, base_delay=0.0))
    assert outcome.succeeded
    assert outcome.retried
    assert len(outcome.attempts) == 3


def test_retries_on_exception():
    calls = {"n": 0}

    def raises_then_ok(_q):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TimeoutError("boom")
        return "1. Open the login page. 2. Reset your password via email link."

    ev = ResponseEvaluator()
    outcome = call_with_retries(raises_then_ok, "How do I reset my password?", ev,
                                RetryPolicy(max_retries=2, base_delay=0.0))
    assert outcome.succeeded
    assert outcome.attempts[0].error is not None


def test_gives_up_after_max_retries():
    ev = ResponseEvaluator()
    outcome = call_with_retries(lambda q: "I don't know.", "Question?", ev,
                                RetryPolicy(max_retries=2, base_delay=0.0))
    assert not outcome.succeeded
    assert len(outcome.attempts) == 3          # 1 + 2 retries


# ---------- metrics: produces quality metrics ----------

def test_aggregator_summary():
    agg = MetricsAggregator()
    agg.record(ResponseRecord("q1", True, 0.9, 1, False, False, 100.0))
    agg.record(ResponseRecord("q2", True, 0.7, 2, True, False, 200.0))
    agg.record(ResponseRecord("q3", False, 0.2, 3, True, True, 300.0))
    s = agg.summary()
    assert s["total"] == 3
    assert s["pass_rate"] == pytest.approx(2 / 3, abs=0.01)
    assert s["failure_rate"] == pytest.approx(1 / 3, abs=0.01)
    assert s["retry_rate"] == pytest.approx(2 / 3, abs=0.01)
    assert 0.5 < s["avg_quality_score"] < 0.7
    assert s["latency_ms_p50"] == 200.0


def test_empty_aggregator():
    assert MetricsAggregator().summary() == {"total": 0}


# ---------- monitor: end-to-end ----------

def test_monitor_end_to_end():
    def model(q):
        return "1. Open Settings. 2. Select API Keys. 3. Create and copy the key."

    mon = ObservabilityMonitor(model)
    for _ in range(5):
        mon.handle("How do I create an API key?")
    report = mon.report()
    assert report["total"] == 5
    assert report["pass_rate"] == 1.0
    assert "avg_quality_score" in report and "latency_ms_p95" in report
