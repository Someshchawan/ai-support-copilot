"""
Response quality evaluation module for AI Support Copilot.

Provides structured evaluation of AI-generated responses using multiple
quality dimensions: completeness, clarity, safety, and reliability.
Each check returns a scored result with actionable feedback, enabling
developers to catch low-quality outputs before they reach end users.

Usage:
    from evals.response_quality import ResponseEvaluator

    evaluator = ResponseEvaluator()
    result = evaluator.evaluate("How do I reset my password?", response_text)
    print(result.summary())
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Quality check result model
# ---------------------------------------------------------------------------

@dataclass
class QualityCheck:
    """Result of a single quality check."""
    name: str
    passed: bool
    score: float          # 0.0 to 1.0
    reason: str


@dataclass
class EvaluationResult:
    """Aggregated result of all quality checks on a single response."""
    user_query: str
    response_text: str
    checks: list[QualityCheck] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Weighted average across all checks, 0.0 to 1.0."""
        if not self.checks:
            return 0.0
        return round(sum(c.score for c in self.checks) / len(self.checks), 2)

    @property
    def passed(self) -> bool:
        """True if overall score meets the minimum quality threshold.
        A failing not_empty check is a hard gate: the response cannot
        pass overall if it is empty or below minimum length."""
        empty_check = next((c for c in self.checks if c.name == "not_empty"), None)
        if empty_check and not empty_check.passed:
            return False
        return self.overall_score >= 0.6

    @property
    def failed_checks(self) -> list[QualityCheck]:
        """Returns only the checks that did not pass."""
        return [c for c in self.checks if not c.passed]

    def summary(self) -> str:
        """Human-readable evaluation summary."""
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"Evaluation: {status} (score: {self.overall_score})",
            f"Query: {self.user_query[:80]}",
            f"Response preview: {self.response_text[:100]}...",
            "",
        ]
        for check in self.checks:
            icon = "PASS" if check.passed else "FAIL"
            lines.append(f"  [{icon}] {check.name} ({check.score}) -- {check.reason}")

        if self.failed_checks:
            lines.append("")
            lines.append(f"Issues found: {len(self.failed_checks)} check(s) failed.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Evaluation engine
# ---------------------------------------------------------------------------

# Phrases that suggest the model is hedging or refusing to answer
UNCERTAINTY_PHRASES = [
    "i'm not sure",
    "i don't know",
    "i cannot",
    "i can't",
    "as an ai",
    "i don't have access",
    "it depends",
    "i am not able to",
    "please consult",
    "i apologize",
]

# Phrases that suggest hallucinated authority or fabricated specifics
HALLUCINATION_SIGNALS = [
    "according to our records",
    "your account shows",
    "i can see that",
    "based on your history",
    "our database indicates",
    "i have checked your",
    "your file shows",
    "our system confirms",
]

# Filler phrases that add no value
FILLER_PHRASES = [
    "great question",
    "that's a great question",
    "sure, i'd be happy to",
    "absolutely",
    "of course",
    "no problem at all",
    "certainly",
]


class ResponseEvaluator:
    """
    Evaluates AI-generated responses across multiple quality dimensions.

    Each evaluation returns an EvaluationResult containing individual
    check scores and an aggregated overall score.
    """

    def __init__(
        self,
        min_length: int = 20,
        max_length: int = 2000,
        min_score_threshold: float = 0.6,
    ) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.min_score_threshold = min_score_threshold

    def evaluate(
        self,
        user_query: str,
        response_text: str,
        expected_keywords: Optional[list[str]] = None,
    ) -> EvaluationResult:
        """
        Run all quality checks on a response and return aggregated results.

        Args:
            user_query: The original user question.
            response_text: The AI-generated response to evaluate.
            expected_keywords: Optional list of terms the response should contain.

        Returns:
            EvaluationResult with individual and overall scores.
        """
        result = EvaluationResult(
            user_query=user_query,
            response_text=response_text,
        )

        result.checks.append(self._check_not_empty(response_text))
        result.checks.append(self._check_length(response_text))
        result.checks.append(self._check_relevance(user_query, response_text))
        result.checks.append(self._check_structure(response_text))
        result.checks.append(self._check_uncertainty(response_text))
        result.checks.append(self._check_hallucination_signals(response_text))
        result.checks.append(self._check_filler_ratio(response_text))
        result.checks.append(self._check_error_leak(response_text))

        if expected_keywords:
            result.checks.append(
                self._check_keyword_coverage(response_text, expected_keywords)
            )

        return result

    # ------------------------------------------------------------------
    # Individual quality checks
    # ------------------------------------------------------------------

    def _check_not_empty(self, response: str) -> QualityCheck:
        """Verify the response is not empty or whitespace only."""
        text = response.strip()
        if not text:
            return QualityCheck("not_empty", False, 0.0, "Response is empty.")
        if len(text) < self.min_length:
            return QualityCheck(
                "not_empty", False, 0.2,
                f"Response is only {len(text)} characters, below the {self.min_length} char minimum."
            )
        return QualityCheck("not_empty", True, 1.0, "Response has sufficient content.")

    def _check_length(self, response: str) -> QualityCheck:
        """Flag responses that are excessively long, which often signals rambling."""
        length = len(response.strip())
        if length > self.max_length:
            return QualityCheck(
                "length", False, 0.3,
                f"Response is {length} chars, exceeding the {self.max_length} char maximum. May be unfocused."
            )
        return QualityCheck("length", True, 1.0, "Response length is within acceptable range.")

    def _check_relevance(self, query: str, response: str) -> QualityCheck:
        """
        Basic relevance check: do significant words from the query appear
        in the response? This is a heuristic, not semantic similarity,
        but catches obvious mismatches.
        """
        stop_words = {
            "i", "me", "my", "the", "a", "an", "is", "are", "was", "were",
            "do", "does", "did", "how", "what", "why", "can", "to", "in",
            "of", "and", "or", "it", "this", "that", "for", "on", "with",
        }
        query_words = {
            w.lower() for w in re.findall(r'\b\w+\b', query)
            if w.lower() not in stop_words and len(w) > 2
        }
        response_lower = response.lower()

        if not query_words:
            return QualityCheck("relevance", True, 0.7, "Query too short for keyword relevance check.")

        matches = sum(1 for w in query_words if w in response_lower)
        ratio = matches / len(query_words)

        if ratio == 0:
            return QualityCheck(
                "relevance", False, 0.0,
                f"None of the query keywords ({', '.join(query_words)}) appear in the response."
            )
        if ratio < 0.3:
            return QualityCheck(
                "relevance", False, 0.3,
                f"Only {matches}/{len(query_words)} query keywords found in response. May be off topic."
            )
        return QualityCheck("relevance", True, round(0.5 + ratio * 0.5, 2), "Response appears relevant to the query.")

    def _check_structure(self, response: str) -> QualityCheck:
        """
        Check whether the response uses any structural formatting
        (numbered steps, bullet points, paragraphs). Structured responses
        are generally more useful for support and how-to queries.
        """
        has_numbered_steps = bool(re.search(r'^\s*\d+[\.\)]\s', response, re.MULTILINE))
        has_bullets = bool(re.search(r'^\s*[-*]\s', response, re.MULTILINE))
        has_multiple_paragraphs = response.strip().count('\n\n') >= 1
        has_headings = bool(re.search(r'^\s*#{1,3}\s', response, re.MULTILINE))

        structure_signals = sum([
            has_numbered_steps, has_bullets,
            has_multiple_paragraphs, has_headings
        ])

        if structure_signals == 0:
            return QualityCheck(
                "structure", False, 0.4,
                "Response lacks formatting structure (no steps, bullets, or paragraphs)."
            )
        return QualityCheck(
            "structure", True, min(1.0, 0.5 + structure_signals * 0.2),
            f"Response uses {structure_signals} structural element(s)."
        )

    def _check_uncertainty(self, response: str) -> QualityCheck:
        """
        Detect hedging or refusal language that suggests the model could
        not confidently answer the question.
        """
        response_lower = response.lower()
        found = [p for p in UNCERTAINTY_PHRASES if p in response_lower]

        if len(found) >= 2:
            return QualityCheck(
                "uncertainty", False, 0.2,
                f"Multiple uncertainty signals detected: {', '.join(found[:3])}. Model may not have a confident answer."
            )
        if len(found) == 1:
            return QualityCheck(
                "uncertainty", True, 0.6,
                f"Minor uncertainty signal: '{found[0]}'. Worth reviewing but not necessarily a problem."
            )
        return QualityCheck("uncertainty", True, 1.0, "No uncertainty signals detected.")

    def _check_hallucination_signals(self, response: str) -> QualityCheck:
        """
        Detect phrases that suggest the model is fabricating specific
        information it could not possibly have (user account data,
        database records, system states).
        """
        response_lower = response.lower()
        found = [p for p in HALLUCINATION_SIGNALS if p in response_lower]

        if found:
            return QualityCheck(
                "hallucination_risk", False, 0.1,
                f"Potential hallucination: response claims access to user data ('{found[0]}'). "
                f"The model has no access to real user records."
            )
        return QualityCheck("hallucination_risk", True, 1.0, "No hallucination signals detected.")

    def _check_filler_ratio(self, response: str) -> QualityCheck:
        """
        Check whether the response starts with or contains excessive
        filler phrases that add no substantive value.
        """
        response_lower = response.lower().strip()
        found = [p for p in FILLER_PHRASES if response_lower.startswith(p)]

        if found:
            return QualityCheck(
                "filler", False, 0.5,
                f"Response starts with filler ('{found[0]}'). Prefer direct, actionable answers."
            )
        return QualityCheck("filler", True, 1.0, "No excessive filler detected.")

    def _check_error_leak(self, response: str) -> QualityCheck:
        """
        Detect raw error messages or stack traces leaking into the
        response, which should never reach an end user.
        """
        error_patterns = [
            r'Traceback \(most recent call last\)',
            r'raise \w+Error',
            r'File ".*\.py"',
            r'requests\.exceptions\.',
            r'KeyError:',
            r'TypeError:',
            r'IndexError:',
            r'JSONDecodeError',
        ]
        for pattern in error_patterns:
            if re.search(pattern, response):
                return QualityCheck(
                    "error_leak", False, 0.0,
                    f"Raw error or stack trace detected in response (pattern: {pattern}). "
                    f"This should never be shown to an end user."
                )
        return QualityCheck("error_leak", True, 1.0, "No error leaks detected.")

    def _check_keyword_coverage(
        self, response: str, expected: list[str]
    ) -> QualityCheck:
        """
        When expected keywords are provided, verify they appear in the
        response. Useful for testing against known-good answers.
        """
        response_lower = response.lower()
        found = [kw for kw in expected if kw.lower() in response_lower]
        missing = [kw for kw in expected if kw.lower() not in response_lower]
        ratio = len(found) / len(expected) if expected else 1.0

        if ratio < 0.5:
            return QualityCheck(
                "keyword_coverage", False, round(ratio, 2),
                f"Missing expected keywords: {', '.join(missing)}"
            )
        return QualityCheck(
            "keyword_coverage", True, round(ratio, 2),
            f"Covered {len(found)}/{len(expected)} expected keywords."
        )


# ---------------------------------------------------------------------------
# Interactive evaluation mode
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the copilot in evaluation mode with live quality scoring."""
    from src.copilot import AISupportCopilot

    print("AI Support Copilot (Evaluation Mode)")
    print("Type 'exit' to quit\n")

    try:
        copilot = AISupportCopilot()
    except ValueError as e:
        print(f"Setup Error: {e}")
        return

    evaluator = ResponseEvaluator()

    while True:
        user_input = input("Ask something: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            print("Please enter a valid question.\n")
            continue

        print("\nThinking...\n")

        response = copilot.get_response(user_input)
        result = evaluator.evaluate(user_input, response)

        print("Response:")
        print(response)
        print()
        print(result.summary())
        print("-" * 60)


if __name__ == "__main__":
    main()
