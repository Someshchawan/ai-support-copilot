import os
import requests


class AISupportCopilot:
    """
    Core class for handling AI-powered support interactions.
    """

    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.api_url = "https://api.openai.com/v1/responses"  # Replace if using Claude API

        if not self.api_key:
            raise ValueError("API_KEY not found. Please set it as an environment variable.")

    def build_prompt(self, user_input, context=None):
        """
        Construct a structured prompt for better AI responses.
        """
        base_prompt = "You are a helpful and concise customer support assistant."

        if context:
            prompt = f"""
{base_prompt}

Context: {context}

User: {user_input}

Provide a clear, step-by-step answer.
"""
        else:
            prompt = f"""
{base_prompt}

User: {user_input}

Provide a clear and helpful answer.
"""

        return prompt.strip()

    def call_api(self, prompt):
        """
        Send request to AI API and return response.
        """
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4.1-mini",
                    "input": prompt,
                },
                timeout=10,
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e)
            }

    def parse_response(self, api_response):
        """
        Extract useful text from API response.
        """
        try:
            return api_response["output"][0]["content"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return "Error: Unable to parse response"

    def get_response(self, user_input, context=None):
        """
        Full pipeline: prompt → API call → response parsing
        """

        if not user_input or not user_input.strip():
            return "Please provide a valid input."

        prompt = self.build_prompt(user_input, context)
        api_response = self.call_api(prompt)

        if isinstance(api_response, dict) and api_response.get("error"):
            return f"API Error: {api_response.get('message')}"

        return self.parse_response(api_response)
