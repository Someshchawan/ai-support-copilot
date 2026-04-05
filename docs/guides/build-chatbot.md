# Build an AI-Powered Chatbot

This guide walks you through building a simple but realistic AI-powered chatbot using the AI Support Copilot.

By the end, you will have a working system that:

* Accepts user input
* Sends structured prompts to an AI API
* Returns useful, contextual responses

---

## 🎯 What you’ll build

A command-line chatbot that:

* Handles user queries
* Uses structured prompts
* Produces consistent and useful responses

---

## 🧱 Step 1: Capture User Input

Start by capturing input from the user:

```python id="u1a2b3"
user_input = input("Ask something: ")
```

This forms the basis of your interaction loop.

---

## 🧠 Step 2: Construct the Prompt

Instead of sending raw input, structure the prompt:

```python id="p4q5r6"
prompt = f"""
You are a helpful and concise customer support assistant.

User: {user_input}

Provide a clear and helpful answer.
"""
```

### Why this matters:

* Defines behavior
* Improves consistency
* Reduces vague responses

### 🆚 Without vs With Structured Prompt

**Without structure:**

```id="n8dj2s"
How do I reset my password?
```

**With structured prompt:**

```id="7sd82k"
You are a helpful support assistant.

User: How do I reset my password?

Provide a clear, step-by-step answer.
```

👉 Structured prompts produce more consistent and useful responses.

---

## 🔌 Step 3: Send Request to API

Send the prompt to your AI provider:

```python id="x7y8z9"
response = copilot.get_response(user_input)
```

Your `ask_ai` function handles:

* Authentication
* Request formatting
* Response parsing

---

## 📤 Step 4: Display the Response

Print the output for the user:

```python id="m3n4o5"
print(response)
```

### ✅ Example Output

```
Response:
1. Go to the login page  
2. Click on "Forgot Password"  
3. Enter your registered email address  
4. Follow the instructions sent to your email  
```

👉 This confirms your chatbot is working correctly.

---

## 🔄 Step 5: Create a Loop (Optional)

To make the chatbot interactive:

```python
from src.copilot import AISupportCopilot

copilot = AISupportCopilot()

while True:
    user_input = input("Ask something (type 'exit' to quit): ").strip()

    if user_input.lower() == "exit":
        break

    if not user_input:
        print("Please enter a valid question.\n")
        continue

    response = copilot.get_response(user_input)

    print("\nResponse:")
    print(response)
    print("-" * 50)
```


---

## ⚠️ Common Issues

### Poor or generic responses

* Add clearer instructions to the prompt
* Include relevant context

### Inconsistent output format

* Specify structure (e.g., “step-by-step answer”)

### Responses not aligned with user intent

* Refine prompt wording
* Test with multiple inputs


---

## 🧪 Improving the Chatbot

To move toward production-quality:

### Add context

```python id="c1d2e3"
context = "User is a premium customer with billing issue"

prompt = f"""
You are a support assistant.

Context: {context}

User: {user_input}
"""
```

---

### Add response evaluation

Use `evals/response_quality.py` to:

* Detect weak responses
* Flag issues
* Improve reliability

---

### Control response behavior

You can guide the model further by:

- Setting tone (e.g., concise, friendly)
- Limiting output length
- Asking for structured formats (lists, steps)

This improves consistency and usability in real-world applications.

---

## 🏗️ System Thinking

This chatbot represents a simplified version of a real AI system:

```id="flow123"
User Input → Prompt Construction → API Call → Response → Evaluation
```

Each step can be improved independently.

---

## 🚀 Next Steps

* Learn how to refine prompts → `docs/concepts/prompts.md`
* Handle real-world API failures → `docs/troubleshooting/api-errors.md`

---

## 🎯 Why this matters

Most AI tutorials stop at “send a request.”

This guide helps you:

* Think in terms of systems
* Improve reliability
* Build features that resemble real-world applications
