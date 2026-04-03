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

---

## 🔌 Step 3: Send Request to API

Send the prompt to your AI provider:

```python id="x7y8z9"
response = ask_ai(prompt)
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

---

## 🔄 Step 5: Create a Loop (Optional)

To make it interactive:

```python id="l6k7j8"
while True:
    user_input = input("Ask something (type 'exit' to quit): ")
    
    if user_input.lower() == "exit":
        break

    prompt = f"""
    You are a helpful support assistant.

    User: {user_input}
    """

    response = ask_ai(prompt)
    print(response)
```

---

## ⚠️ Common Issues

### Generic or poor responses

* Improve prompt clarity
* Add context

### Repetitive answers

* Adjust instructions
* Refine prompt structure

### Unexpected output format

* Specify output format explicitly

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
