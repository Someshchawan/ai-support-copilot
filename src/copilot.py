"""
Core module for the AI Support Copilot.

Handles prompt construction, API communication, response parsing,
and error recovery. Designed to demonstrate production patterns
including structured prompts, retry with exponential backoff,
and separation of system and user roles.

Usage:
    from src.copilot import AISupportCopilot

    copilot = AISupportCopilot()
    response = copilot.get_response("How do I reset my password?")
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Optional

import requests

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful, accurate, and concise customer support assistant. "
    "Always provide step-by-step instructions when applicable. "
    "If you do not have enough information to answer confidently, "
    "say so clearly rather than guessing. "
    "Never fabricate account details, transaction records, or system states."
)

USER_PROMPT_WITH_CONTEXT = (
    "Context: {context}\n\n"
    "Question: {user_input}\n\n"
    "Provide a clear, step-by-step answer."
)

USER_PROMPT_WITHOUT_CONTEXT = (
    "Question: {user_input}\n\n"
    "Provide a clear and helpful answer."
)

# ---------------------------------------------------------------------------
# Retry configuration
# ---------------------------------------------------------------------------

MAX_RETRIES: int = 3
INITIAL_BACKOFF_SECONDS: float = 1.0
BACKOFF_MULTIPLIER: float = 2.0
RETRYABLE_STATUS_CODES: set[int] = {429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class AISupportCopilot:
    """
    Production-style AI support assistant demonstrating structured prompts,
    retry logic, and response parsing.

    The pipeline follows four stages:
        1. Prompt construction (system + user role separation)
        2. API call with retry and exponential backoff
        3. Response parsing
        4. Error handling at every stage
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.openai.com/v1/chat/completions",
        model: str = "gpt-4.1-mini",
        timeout: int = 15,
    ) -> None:
        self.api_key: str = api_key or os.getenv("API_KEY", "")
        self.api_url: str = api_url
        self.model: str = model
        self.timeout: int = timeout

        if not self.api_key:
            raise ValueError(
                "API_KEY not found. Set it as an environment variable "
                "or pass it directly: AISupportCopilot(api_key='your_key')"
            )

    # ------------------------------------------------------------------
    # Stage 1: Prompt construction
    # ------------------------------------------------------------------

    def build_prompt(
        self,
        user_input: str,
        context: Optional[str] = None,
    ) -> list[dict[str, str]]:
        """
        Build a structured messages array with separated system and user roles.

        This separation matters because:
          - The system message defines HOW the model should behave.
          - The user message contains WHAT the user is asking.
          - Mixing both into a single string produces less consistent results.

        Args:
            user_input: The end user's question.
            context: Optional background information for the query.

        Returns:
            A list of message dicts ready for the chat completions API.
        """
        if context:
            user_content = USER_PROMPT_WITH_CONTEXT.format(
                context=context,
                user_input=user_input,
            )
        else:
            user_content = USER_PROMPT_WITHOUT_CONTEXT.format(
                user_input=user_input,
            )

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    # ------------------------------------------------------------------
    # Stage 2: API call with retry
    # ------------------------------------------------------------------

    def call_api(
        self,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
        """
        Send a request to the AI API with automatic retry and exponential
        backoff for transient errors (429 rate limits, 5xx server errors).

        Args:
            messages: The structured messages array from build_prompt.

        Returns:
            The parsed JSON response from the API, or an error dict.
        """
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    "API request attempt %d/%d to %s",
                    attempt, MAX_RETRIES, self.api_url,
                )

                response = requests.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                    },
                    timeout=self.timeout,
                )

                # If we get a retryable status code, log and retry
                if response.status_code in RETRYABLE_STATUS_CODES:
                    logger.warning(
                        "Received %d on attempt %d/%d. Retrying in %.1fs...",
                        response.status_code, attempt, MAX_RETRIES, backoff,
                    )
                    if attempt < MAX_RETRIES:
                        time.sleep(backoff)
                        backoff *= BACKOFF_MULTIPLIER
                        continue

                    # Final attempt also failed
                    return {
                        "error": True,
                        "status_code": response.status_code,
                        "message": (
                            f"API returned {response.status_code} after "
                            f"{MAX_RETRIES} attempts. Last response: "
                            f"{response.text[:200]}"
                        ),
                    }

                # Non-retryable HTTP errors (401 auth, 400 bad request, etc.)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(
                    "Request timed out on attempt %d/%d.", attempt, MAX_RETRIES,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= BACKOFF_MULTIPLIER
                    continue
                return {
                    "error": True,
                    "message": f"Request timed out after {MAX_RETRIES} attempts.",
                }

            except requests.exceptions.ConnectionError as exc:
                logger.error("Connection error: %s", exc)
                if attempt < MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= BACKOFF_MULTIPLIER
                    continue
                return {
                    "error": True,
                    "message": f"Connection failed after {MAX_RETRIES} attempts: {exc}",
                }

            except requests.exceptions.HTTPError as exc:
                logger.error("HTTP error (non-retryable): %s", exc)
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": str(exc),
                }

            except requests.exceptions.RequestException as exc:
                logger.error("Unexpected request error: %s", exc)
                return {
                    "error": True,
                    "message": f"Unexpected error: {exc}",
                }

        # Should not reach here, but safety net
        return {"error": True, "message": "All retry attempts exhausted."}

    # ------------------------------------------------------------------
    # Stage 3: Response parsing
    # ------------------------------------------------------------------

    def parse_response(self, api_response: dict[str, Any]) -> str:
        """
        Extract the assistant's message text from the API response.

        Handles the standard OpenAI chat completions response format:
            response["choices"][0]["message"]["content"]

        Args:
            api_response: The raw JSON response from the API.

        Returns:
            The extracted text, or a descriptive error message.
        """
        try:
            return api_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            logger.error("Failed to parse API response: %s", exc)
            logger.debug("Raw response: %s", api_response)
            return "Error: Unable to parse the API response. The response format may have changed."

    # ------------------------------------------------------------------
    # Stage 4: Full pipeline
    # ------------------------------------------------------------------

    def get_response(
        self,
        user_input: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Run the full pipeline: validate input, build prompt, call API,
        parse response.

        This is the primary method consumers of this class should use.

        Args:
            user_input: The end user's question.
            context: Optional background information for the query.

        Returns:
            The AI-generated response text, or an error message.
        """
        if not user_input or not user_input.strip():
            return "Please provide a valid input."

        messages = self.build_prompt(user_input, context)
        api_response = self.call_api(messages)

        if isinstance(api_response, dict) and api_response.get("error"):
            error_msg = api_response.get("message", "Unknown error")
            logger.error("Pipeline error: %s", error_msg)
            return f"API Error: {error_msg}"

        return self.parse_response(api_response)
