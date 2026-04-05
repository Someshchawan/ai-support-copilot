# Prompt Design

Prompt design is one of the most critical aspects of building reliable AI-powered applications.

A well-structured prompt can significantly improve response quality, while a poorly designed prompt can lead to vague, incorrect, or inconsistent outputs.

---

## 🧠 What is a prompt?

A prompt is the structured input provided to an AI model to guide its response.

It typically includes:

* Instructions (what the model should do)
* Context (relevant background information)
* User input (the actual query)

---

## 🧠 Prompt as an Interface

In AI systems, the prompt acts as the **interface between your application and the model**.

Unlike traditional APIs where behavior is fixed, prompts define:

* How the model behaves
* What context it considers
* How responses are structured

This means prompt design is not just input formatting—it is **system design**.

---

## 🧩 Basic Prompt Structure

A simple prompt can be structured as:

```id="7h4r5m"
You are a support assistant.

Context: User is facing an issue with login.

User: How do I reset my password?
```

---

## ❌ Example: Poor Prompt

```id="6a9z2k"
How do I reset my password?
```

### Problems:

* No role definition
* No context
* No guidance on response style

👉 Result: Generic or inconsistent answers

---

## ✅ Example: Improved Prompt

```id="q4m8x1"
You are a helpful and concise customer support assistant.

Context: The user is having trouble logging into their account.

User: How do I reset my password?

Provide a clear, step-by-step answer.
```

### Improvements:

* Defines assistant behavior
* Adds context
* Specifies response format

👉 Result: More structured and useful output

---

### 🆚 Output Comparison

**Poor Prompt Output:**

```
You can reset your password from the login page.
```

**Improved Prompt Output:**

```
1. Go to the login page  
2. Click on "Forgot Password"  
3. Enter your registered email address  
4. Follow the instructions sent to your email  
```

👉 Better prompts produce more structured, actionable responses.

---

## 🎯 Key Principles

### 1. Be explicit

Clearly tell the model what to do.

### 2. Provide context

Relevant context improves accuracy and relevance.

### 3. Define output expectations

Specify tone, format, or constraints.

### 4. Reduce ambiguity

Avoid vague or incomplete instructions.

### 5. Add constraints

Limit the model’s behavior when needed.

Example:
- “Answer in 3 steps”
- “Do not assume missing information”

---

## ⚠️ Common Failure Modes

### Hallucinations

The model generates incorrect or made-up information.

### Irrelevant responses

The output does not match the user’s intent.

### Overly verbose answers

The response is too long or unfocused.

### Inconsistent tone

The style of response changes unpredictably.

---

## 🛠️ Improving Prompts Iteratively

Prompt design is not a one-time task.

A typical workflow:

1. Start with a basic prompt
2. Test with real inputs
3. Identify failure cases
4. Refine instructions and context
5. Repeat

---

## 🔗 Connection to This Project

In this project:

* Prompts are constructed in `src/copilot.py`
* Context can be injected dynamically
* Output quality can be evaluated using `evals/response_quality.py`

---

## 🚀 Next Steps

* Apply these concepts while building the chatbot → `docs/guides/build-chatbot.md`
* Learn how to handle failures → `docs/troubleshooting/api-errors.md`

---

## 🎯 Why this matters

In AI systems, the quality of the output is directly influenced by the quality of the prompt.

Understanding prompt design is essential for building:

* Reliable systems
* Predictable outputs
* Better developer and user experiences

