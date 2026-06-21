![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen)

# AI Support Copilot

A production-style AI support assistant designed to demonstrate how developers can build, evaluate, and improve real-world AI-powered features using modern API workflows.

This is not a wrapper around an API call. It is a complete system with structured prompts, retry logic, response parsing, and an evaluation layer that catches hallucinations, uncertainty, irrelevance, and error leaks before they reach an end user.

---

## Why this project exists

AI APIs make it easy to generate responses, but building **reliable, production-ready AI systems** is much harder.

Developers often struggle with:

* Designing effective prompts with proper system and user role separation
* Handling inconsistent or low-quality responses
* Debugging API failures, rate limits, and edge cases
* Knowing when an AI response is confidently wrong

This project bridges that gap. It provides a **structured, developer-first approach** to building an AI support assistant, focused not just on implementation, but on **reliability, evaluation, and learning**.

---

## What you'll build

A realistic **AI-powered support copilot** that:

* Accepts user queries and constructs structured prompts with system/user role separation
* Calls the API with automatic retry and exponential backoff for rate limits
* Parses responses and handles failures gracefully
* Evaluates every response across 8 quality dimensions before showing it to a user

---

## Example interaction

**User:**

```
How do I reset my password?
```

**Response:**

```
1. Go to the login page
2. Click on "Forgot Password"
3. Enter your registered email address
4. Follow the instructions sent to your email to reset your password
```

**Evaluation:**

```
Evaluation: PASS (score: 0.93)
  [PASS] not_empty (1.0) -- Response has sufficient content.
  [PASS] length (1.0) -- Response length is within acceptable range.
  [PASS] relevance (0.75) -- Response appears relevant to the query.
  [PASS] structure (0.9) -- Response uses 2 structural element(s).
  [PASS] uncertainty (1.0) -- No uncertainty signals detected.
  [PASS] hallucination_risk (1.0) -- No hallucination signals detected.
  [PASS] filler (1.0) -- No excessive filler detected.
  [PASS] error_leak (1.0) -- No error leaks detected.
```

---

## Evaluation in action: catching a bad response

The evaluation layer is not theoretical. Here is a concrete example of it catching a hallucinated response:

**User:** "Why was I charged twice?"

**Bad AI response:**

```
I can see that your account shows two transactions on June 15.
According to our records, the first charge was processed correctly
and the second was a duplicate.
```

**Evaluation result:**

```
Evaluation: FAIL (score: 0.49)
  [FAIL] hallucination_risk (0.1) -- Potential hallucination: response claims
         access to user data ('i can see that'). The model has no access to
         real user records.
  [FAIL] filler (0.5) -- Response starts with filler. Prefer direct, actionable answers.

Issues found: 2 check(s) failed.
```

The model fabricated access to account data it does not have. The evaluation layer catches this before it reaches the user, which is exactly the kind of quality gate production AI systems need.

---

## System flow

```mermaid
graph TD
    A[User Query] --> B[Prompt Builder]
    B --> C{System + User Role Separation}
    C --> D[API Call with Retry]
    D --> E{Rate Limit / Error?}
    E -->|Yes| F[Exponential Backoff]
    F --> D
    E -->|No| G[Response Parser]
    G --> H[Evaluation Layer]
    H --> I{Pass 8 Quality Checks?}
    I -->|Yes| J[Final Output]
    I -->|No| K[Flag Issues]
```

---

## Project structure

```
ai-support-copilot/
│
├── docs/
│   ├── quickstart.md              # Get started quickly
│   ├── concepts/
│   │   └── prompts.md             # Prompt design fundamentals
│   ├── guides/
│   │   └── build-chatbot.md       # Step-by-step implementation
│   └── troubleshooting/
│       └── api-errors.md          # Common issues and fixes
│
├── src/
│   └── copilot.py                 # Core AI interaction logic
│
├── examples/
│   └── basic_chat.py              # Simple usage example
│
├── evals/
│   └── response_quality.py        # 8-dimension evaluation system
│
├── tests/
│   └── test_evaluation.py         # 17 tests proving evaluation works
│
└── requirements.txt               # Project dependencies
```

---

## Quickstart

1. Clone the repository

```bash
git clone https://github.com/Someshchawan/ai-support-copilot.git
cd ai-support-copilot
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set your API key

```bash
export API_KEY="your_api_key_here"
```

4. Run the example

```bash
python examples/basic_chat.py
```

5. Run with evaluation mode

```bash
python evals/response_quality.py
```

For detailed setup, see [Quickstart Guide](docs/quickstart.md)

---

## Developer learning path

Navigate the project based on what you want to do:

**Get started**
* [Quickstart](docs/quickstart.md) — Run your first AI interaction

**Learn core concepts**
* [Prompt Design](docs/concepts/prompts.md) — Structure inputs for better outputs

**Build features**
* [Build a Chatbot](docs/guides/build-chatbot.md) — Step-by-step implementation

**Handle failures**
* [API Errors & Troubleshooting](docs/troubleshooting/api-errors.md) — Debug real-world issues

**Explore the code**
* [`src/copilot.py`](src/copilot.py) — Core AI interaction logic with retry and backoff
* [`examples/basic_chat.py`](examples/basic_chat.py) — Working CLI example

**Evaluate output quality**
* [`evals/response_quality.py`](evals/response_quality.py) — 8-dimension evaluation system
* [`tests/test_evaluation.py`](tests/test_evaluation.py) — 17 tests proving evaluation catches real issues

---

## Key concepts covered

### Prompt design
* System and user role separation
* Structured prompt templates
* Context injection for better accuracy

### Retry and error handling
* Exponential backoff for rate limits (429)
* Separate handling for timeouts, connection errors, and HTTP errors
* Structured logging at every stage

### Response evaluation (8 checks)
* **not_empty** — catches empty or too-short responses
* **length** — flags excessively long, unfocused output
* **relevance** — verifies query keywords appear in the response
* **structure** — checks for steps, bullets, or paragraphs
* **uncertainty** — detects hedging language ("I'm not sure," "as an AI")
* **hallucination_risk** — catches fabricated claims about user data
* **filler** — flags empty pleasantries ("Great question!")
* **error_leak** — blocks raw stack traces from reaching users

### Failure modes
* API errors (authentication, rate limits, timeouts)
* Hallucinated or fabricated responses
* Off-topic or irrelevant answers
* Raw error messages leaking to end users

---

## Running tests

```bash
python -m pytest tests/test_evaluation.py -v
```

Expected output:

```
17 passed in 0.05s
```

The test suite demonstrates each evaluation check catching a real, concrete failure mode, from fabricated account data to leaked stack traces to completely off-topic responses.

---

## Design philosophy

* **Developer Experience (DX)** — Clear onboarding and structure
* **Progressive Learning** — From simple usage to deeper concepts
* **Real-world relevance** — Focus on practical use cases and actual failure modes
* **System thinking** — Not just "call API", but "build a reliable feature"
* **Evaluation as a first-class concern** — AI output must be monitored, not assumed correct

---

## Who this is for

* Developers building AI-powered features for the first time
* Engineers who want to move beyond "call the API" to production-quality systems
* Technical writers and DevRel professionals exploring AI documentation
* Anyone interested in improving AI reliability and usability in products

---

## Future improvements

* Context-aware responses using external data (RAG)
* LLM-as-judge evaluation using a second model call for semantic scoring
* Streaming responses and latency handling
* Tool usage and agent-based workflows
* Deployed documentation site with CI-tested code samples

---

## Author

**Somesh Chawan**
Developer Experience | Technical Documentation | AI Systems

Building developer-first documentation systems, API learning experiences, and AI-assisted content workflows.

* [LinkedIn](https://linkedin.com/in/somesh-chawan-b29144148)
* [GitHub](https://github.com/Someshchawan)

---

## License

MIT License
