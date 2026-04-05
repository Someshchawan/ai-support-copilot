## ⚡ Quickstart

Get the AI Support Copilot running locally in under 2 minutes.

---

### ⚡ Prerequisites

Before you begin, ensure you have:

* Python 3.9+
* An API key (Claude / OpenAI-compatible API)

---

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai-support-copilot.git
cd ai-support-copilot
```

---

### 2. Set your API key

Set your API key as an environment variable:

#### macOS / Linux

```bash
export API_KEY="your_api_key_here"
```

#### Windows (PowerShell)

```bash
setx API_KEY "your_api_key_here"
```

> 💡 The application reads your API key securely from the environment.

---

### 3. Run the example

```bash
python examples/basic_chat.py
```

---

### 4. Try your first query

You’ll see:

```
Ask something:
```

Try:

```
How do I reset my password?
```

---

### ✅ Expected Output

```
Response:
1. Go to the login page  
2. Click on "Forgot Password"  
3. Enter your registered email address  
4. Follow the instructions sent to your email  
```

---

### 🎯 What just happened?

* Your input was converted into a structured prompt
* The AI API generated a response
* The system parsed and returned a clean output

---

### ⚠️ Having Issues?

If something doesn’t work as expected, see:

👉 [API Errors & Troubleshooting](docs/troubleshooting/api-errors.md)

---

### 🚀 Next Steps

* Learn prompt design → [Prompt Design](docs/concepts/prompts.md)
* Build a chatbot → [Build a Chatbot](docs/guides/build-chatbot.md)
* Explore full project → [Developer Learning Path](../README.md#-developer-learning-path)
