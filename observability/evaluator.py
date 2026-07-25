"""Response evaluator: *measures response quality* and *detects failures*.

Scores a model response across several heuristic dimensions and returns an
EvaluationResult. A response "fails" when its aggregate score falls below a
configurable threshold, or when a hard failure signal is present (empty output,
error marker, refusal/fallback).

The heuristics are intentionally transparent and dependency-free so the layer
runs deterministically in CI without calling a real model.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

# Signals that a response is a non-answer / failure.
_FALLBACK_PATTERNS = [
    r"\bi (?:do not|don't) know\b",
    r"\bi'?m not sure\b",
    r"\bi cannot help\b",
    r"\bunable to (?:answer|help|assist)\b",
    r"\bas an ai\b.*\bcannot\b",
    r"\bsomething went wrong\b",
    r"\berror\b.*\btry again\b",
]
_ERROR_MARKERS = ["<error>", "traceback", "null", "none"]

_STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
    "is", "are", "how", "do", "i", "my", "you", "your", "it", "this", "that",
}


@dataclass
class EvaluationResult:
    passed: bool
    score: float                       # 0.0 - 1.0
    reasons: List[str] = field(default_factory=list)
    failure: bool = False              # hard failure (not just low quality)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "score": round(self.score, 3),
            "reasons": self.reasons,
            "failure": self.failure,
        }


class ResponseEvaluator:
    """Scores responses and flags failures against a quality threshold."""

    def __init__(self, threshold: float = 0.6, min_length: int = 20) -> None:
        self.threshold = threshold
        self.min_length = min_length

    def _keywords(self, text: str) -> set:
        words = re.findall(r"[a-zA-Z']+", text.lower())
        return {w for w in words if w not in _STOPWORDS and len(w) > 2}

    def evaluate(self, query: str, response: str) -> EvaluationResult:
        reasons: List[str] = []
        response = (response or "").strip()

        # --- hard failure signals -> score 0, failure=True ---
        if not response:
            return EvaluationResult(False, 0.0, ["empty response"], failure=True)

        low = response.lower()
        if any(marker in low for marker in _ERROR_MARKERS):
            return EvaluationResult(False, 0.0, ["error marker in response"], failure=True)

        for pat in _FALLBACK_PATTERNS:
            if re.search(pat, low):
                return EvaluationResult(
                    False, 0.15, ["fallback / non-answer detected"], failure=True
                )

        # --- graded quality dimensions (each contributes to the score) ---
        score = 0.0

        # 1. Length adequacy (0.30)
        if len(response) >= self.min_length:
            score += 0.30
        else:
            reasons.append(f"response too short ({len(response)} chars)")
            score += 0.30 * (len(response) / self.min_length)

        # 2. Relevance: keyword overlap with the query (0.40)
        q_kw, r_kw = self._keywords(query), self._keywords(response)
        if q_kw:
            overlap = len(q_kw & r_kw) / len(q_kw)
            score += 0.40 * overlap
            if overlap < 0.25:
                reasons.append("low relevance to query")
        else:
            score += 0.40  # nothing to match against; don't penalize

        # 3. Structure / actionability: steps, lists, or clear sentences (0.20)
        if re.search(r"(^\s*\d+\.|\n\s*[-*]\s|\bstep\b)", response, re.IGNORECASE):
            score += 0.20
        elif response.count(".") >= 1:
            score += 0.12
        else:
            reasons.append("no clear structure")

        # 4. No hedging noise (0.10)
        if not re.search(r"\b(maybe|perhaps|possibly|i think)\b", low):
            score += 0.10
        else:
            reasons.append("hedging language")

        score = max(0.0, min(1.0, score))
        passed = score >= self.threshold
        if not passed and "low quality" not in reasons:
            reasons.append(f"below quality threshold ({score:.2f} < {self.threshold})")
        return EvaluationResult(passed, score, reasons, failure=not passed and score < 0.3)
