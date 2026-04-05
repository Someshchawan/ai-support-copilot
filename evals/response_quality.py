"""
Basic evaluation module for assessing AI response quality.

This provides a simplified approach to demonstrate how developers can
detect low-quality or unreliable outputs in AI systems.
"""

from src.copilot import AISupportCopilot


def evaluate_response(response):
    """
    Basic heuristic evaluation of response quality.
    """
    if not response or len(response.strip()) < 10:
        return "⚠️ Low-quality response"

    if "Error" in response:
        return "❌ API or parsing issue"

    return "✅ Response looks reasonable"


def main():
    print("🤖 AI Support Copilot (Evaluation Mode)")
    print("Type 'exit' to quit\n")

    try:
        copilot = AISupportCopilot()
    except ValueError as e:
        print(f"Setup Error: {e}")
        return

    while True:
        user_input = input("Ask something: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye! 👋")
            break

        if not user_input:
            print("Please enter a valid question.\n")
            continue

        print("\nThinking...\n")

        response = copilot.get_response(user_input)
        evaluation = evaluate_response(response)

        print("Response:")
        print(response)
        print("\nEvaluation:")
        print(evaluation)
        print("-" * 50)


if __name__ == "__main__":
    main()
