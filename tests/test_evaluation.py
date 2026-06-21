"""
Tests for the response quality evaluation system.

These tests demonstrate real failure modes the evaluator catches,
serving as both a test suite and a concrete proof that the evaluation
layer works as documented.

Run with: python -m pytest tests/test_evaluation.py -v
"""

import sys
import os

# Ensure project root is on the path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evals.response_quality import ResponseEvaluator, EvaluationResult


evaluator = ResponseEvaluator()


# ---------------------------------------------------------------------------
# Tests: Good responses should pass
# ---------------------------------------------------------------------------

class TestGoodResponses:
    """Verify that well-formed responses pass evaluation."""

    def test_structured_step_by_step_response(self):
        query = "How do I reset my password?"
        response = (
            "To reset your password, follow these steps:\n\n"
            "1. Go to the login page\n"
            "2. Click on 'Forgot Password'\n"
            "3. Enter your registered email address\n"
            "4. Check your email for a reset link\n"
            "5. Create a new password and confirm it"
        )
        result = evaluator.evaluate(query, response)
        assert result.passed, f"Expected PASS but got FAIL:\n{result.summary()}"
        assert result.overall_score >= 0.7

    def test_response_with_relevant_keywords(self):
        query = "How do I configure SSL certificates?"
        response = (
            "To configure SSL certificates for your server:\n\n"
            "1. Generate a certificate signing request (CSR)\n"
            "2. Submit the CSR to a certificate authority\n"
            "3. Install the SSL certificate on your server\n"
            "4. Update your server configuration to use HTTPS\n"
            "5. Test the connection to verify SSL is working"
        )
        result = evaluator.evaluate(query, response)
        assert result.passed
        # Check that relevance specifically passed
        relevance = next(c for c in result.checks if c.name == "relevance")
        assert relevance.passed


# ---------------------------------------------------------------------------
# Tests: Catching empty or too-short responses
# ---------------------------------------------------------------------------

class TestEmptyResponses:
    """The evaluator should catch empty or near-empty outputs."""

    def test_completely_empty_response(self):
        result = evaluator.evaluate("How do I reset my password?", "")
        assert not result.passed
        # The not_empty check specifically must fail
        empty_check = next(c for c in result.checks if c.name == "not_empty")
        assert not empty_check.passed
        assert empty_check.score == 0.0

    def test_whitespace_only_response(self):
        result = evaluator.evaluate("How do I reset my password?", "   \n\n  ")
        assert not result.passed

    def test_too_short_response(self):
        result = evaluator.evaluate("How do I reset my password?", "Try again.")
        not_empty = next(c for c in result.checks if c.name == "not_empty")
        assert not not_empty.passed


# ---------------------------------------------------------------------------
# Tests: Catching hallucinations
# ---------------------------------------------------------------------------

class TestHallucinationDetection:
    """
    The evaluator should flag responses where the model fabricates
    access to user data it could not possibly have.
    """

    def test_fabricated_account_access(self):
        query = "Why was I charged twice?"
        response = (
            "I can see that your account shows two transactions "
            "on June 15. According to our records, the first charge "
            "was processed correctly and the second was a duplicate."
        )
        result = evaluator.evaluate(query, response)
        hallucination = next(c for c in result.checks if c.name == "hallucination_risk")
        assert not hallucination.passed, (
            "Evaluator should flag fabricated claims about user account data"
        )
        assert hallucination.score <= 0.2

    def test_clean_response_no_hallucination(self):
        query = "Why was I charged twice?"
        response = (
            "Duplicate charges can happen for several reasons:\n\n"
            "1. A temporary hold that appears as a second charge\n"
            "2. A processing error during payment\n"
            "3. An accidental double submission\n\n"
            "Contact your bank to check if one is a pending hold. "
            "If both are confirmed charges, reach out to our support team."
        )
        result = evaluator.evaluate(query, response)
        hallucination = next(c for c in result.checks if c.name == "hallucination_risk")
        assert hallucination.passed


# ---------------------------------------------------------------------------
# Tests: Catching uncertainty and refusal
# ---------------------------------------------------------------------------

class TestUncertaintyDetection:
    """The evaluator should flag excessive hedging or refusal language."""

    def test_multiple_uncertainty_signals(self):
        query = "How do I export my data?"
        response = (
            "I'm not sure about the exact steps for your specific setup. "
            "I don't have access to your account details, so I can't "
            "provide specific instructions. It depends on your plan level."
        )
        result = evaluator.evaluate(query, response)
        uncertainty = next(c for c in result.checks if c.name == "uncertainty")
        assert not uncertainty.passed

    def test_single_minor_uncertainty_is_acceptable(self):
        query = "How do I export my data?"
        response = (
            "It depends on whether you are using the free or premium plan.\n\n"
            "For free plans:\n"
            "1. Go to Settings\n"
            "2. Click Export\n"
            "3. Select CSV format\n\n"
            "For premium plans, you also have JSON and XML options."
        )
        result = evaluator.evaluate(query, response)
        uncertainty = next(c for c in result.checks if c.name == "uncertainty")
        # Single "it depends" with actionable follow-up is acceptable
        assert uncertainty.passed


# ---------------------------------------------------------------------------
# Tests: Catching error leaks
# ---------------------------------------------------------------------------

class TestErrorLeakDetection:
    """Raw errors or stack traces should never appear in user responses."""

    def test_stack_trace_in_response(self):
        query = "What is my account balance?"
        response = (
            'Traceback (most recent call last):\n'
            '  File "copilot.py", line 42, in call_api\n'
            '    response.raise_for_status()\n'
            'requests.exceptions.HTTPError: 500 Server Error'
        )
        result = evaluator.evaluate(query, response)
        error_leak = next(c for c in result.checks if c.name == "error_leak")
        assert not error_leak.passed
        assert error_leak.score == 0.0

    def test_clean_error_message_is_fine(self):
        query = "What is my account balance?"
        response = (
            "We are currently experiencing a temporary service issue. "
            "Please try again in a few minutes. If the problem continues, "
            "contact our support team for assistance."
        )
        result = evaluator.evaluate(query, response)
        error_leak = next(c for c in result.checks if c.name == "error_leak")
        assert error_leak.passed


# ---------------------------------------------------------------------------
# Tests: Catching irrelevant responses
# ---------------------------------------------------------------------------

class TestRelevanceDetection:
    """The evaluator should flag responses that ignore the user's question."""

    def test_completely_off_topic(self):
        query = "How do I reset my password?"
        response = (
            "Our company was founded in 2015 and has grown to serve "
            "over 10 million users worldwide. We offer a range of "
            "products designed to enhance productivity and collaboration."
        )
        result = evaluator.evaluate(query, response)
        relevance = next(c for c in result.checks if c.name == "relevance")
        assert not relevance.passed

    def test_relevant_response_passes(self):
        query = "How do I reset my password?"
        response = (
            "To reset your password:\n\n"
            "1. Visit the login page\n"
            "2. Click 'Forgot Password'\n"
            "3. Enter your email to receive a reset link"
        )
        result = evaluator.evaluate(query, response)
        relevance = next(c for c in result.checks if c.name == "relevance")
        assert relevance.passed


# ---------------------------------------------------------------------------
# Tests: Filler detection
# ---------------------------------------------------------------------------

class TestFillerDetection:
    """Responses should not start with empty pleasantries."""

    def test_filler_opening(self):
        query = "How do I cancel my subscription?"
        response = (
            "Great question! To cancel your subscription, go to "
            "Settings and click Cancel Plan."
        )
        result = evaluator.evaluate(query, response)
        filler = next(c for c in result.checks if c.name == "filler")
        assert not filler.passed

    def test_direct_opening(self):
        query = "How do I cancel my subscription?"
        response = (
            "To cancel your subscription:\n\n"
            "1. Go to Settings\n"
            "2. Select Billing\n"
            "3. Click Cancel Plan\n"
            "4. Confirm the cancellation"
        )
        result = evaluator.evaluate(query, response)
        filler = next(c for c in result.checks if c.name == "filler")
        assert filler.passed


# ---------------------------------------------------------------------------
# Tests: Keyword coverage (optional expected terms)
# ---------------------------------------------------------------------------

class TestKeywordCoverage:
    """When expected keywords are provided, verify coverage."""

    def test_missing_critical_keywords(self):
        query = "How do I configure SMTP for email notifications?"
        response = "Go to the settings page and update your preferences."
        result = evaluator.evaluate(
            query, response,
            expected_keywords=["SMTP", "email", "port", "authentication"]
        )
        coverage = next(c for c in result.checks if c.name == "keyword_coverage")
        assert not coverage.passed

    def test_good_keyword_coverage(self):
        query = "How do I configure SMTP for email notifications?"
        response = (
            "To configure SMTP for email notifications:\n\n"
            "1. Go to Settings > Email\n"
            "2. Enter your SMTP server address and port\n"
            "3. Provide your authentication credentials\n"
            "4. Send a test email to verify the configuration"
        )
        result = evaluator.evaluate(
            query, response,
            expected_keywords=["SMTP", "email", "port", "authentication"]
        )
        coverage = next(c for c in result.checks if c.name == "keyword_coverage")
        assert coverage.passed
