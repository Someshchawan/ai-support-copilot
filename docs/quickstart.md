# Quickstart

This guide helps you run the AI Support Copilot locally and make your **first successful AI API call in under 5 minutes**.

---

## 🎯 What you’ll achieve

By the end of this guide, you will:

* Make your first AI-powered API call
* Understand the basic request → response flow
* Run a working AI support interaction locally

---

## ⚡ Prerequisites

* Python 3.9+
* An API key from your AI provider (e.g., OpenAI or Claude-compatible API)
* Basic familiarity with running Python scripts

---

## 📦 Step 1: Clone the repository

```bash
git clone https://github.com/<your-username>/ai-support-copilot.git
cd ai-support-copilot
```

---

## 🔑 Step 2: Set your API key

Set your API key as an environment variable:

### macOS / Linux

```bash
export API_KEY="your_api_key_here"
```

### Windows (PowerShell)

```bash
setx API_KEY "your_api_key_here"
```

> 💡 **Why this matters**
> The application reads your API key securely from the environment instead of hardcoding it in the code.

---

## ▶️ Step 3: Run the example

```bash
python examples/basic_chat.py
```

You should see:

```
Ask something:
```

Try asking:

```
How do I reset my password?
```

---

## 🧠 What just happened?

You just executed the **core AI application flow**:

1. Your input was captured from the terminal
2. It was sent to an AI API
3. A prompt was constructed internally
4. The model generated a response
5. The response was returned and displayed

This is the foundation of most AI-powered applications.

---

## ⚠️ Common Issues

### ❌ API key not found

* Ensure the environment variable is set correctly
* Restart your terminal after setting it

---

### ❌ Empty or unexpected response

* Verify your API key is valid
* Check internet connectivity
* Ensure your request format is correct

---

### ❌ Slow or inconsistent responses

* AI responses can vary depending on input
* This will be addressed in later sections (prompt design & evaluation)

---

## 🚀 Next Steps

Now that you’ve completed your first successful run:

* Learn how prompts shape responses → `docs/concepts/prompts.md`
* Build a structured chatbot → `docs/guides/build-chatbot.md`
* Handle real-world API failures → `docs/troubleshooting/api-errors.md`

---

## 📊 Success Criteria

You have successfully completed this guide if:

* You ran the script without errors
* You received a valid AI response
* You understand the basic request → response flow

---

## 🎯 Why this guide exists

Developers often get stuck at the very first step—configuring APIs and making the initial call.

This guide is designed to:

* Reduce friction
* Accelerate onboarding
* Build early confidence

So you can move quickly toward building real AI-powered features.
