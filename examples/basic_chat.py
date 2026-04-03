from src.copilot import AISupportCopilot

def main():
print("🤖 AI Support Copilot")
print("Type 'exit' to quit\n")

```
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

    print("Response:")
    print(response)
    print("-" * 50)
```

if **name** == "**main**":
main()

