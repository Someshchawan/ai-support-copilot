# AI Support Copilot (Production-Style Developer Education Project)

A production-style AI support assistant that demonstrates how developers can build, **evaluate, and monitor** real-world AI-powered features using modern API workflows — including an **evaluation & observability layer** that measures response quality, detects failures, triggers retries, and produces quality metrics.

---

## 🧠 Why this project exists

AI APIs make it easy to generate responses — but building **reliable, production-ready AI systems** is much harder. Developers struggle with prompt design, inconsistent or low-quality responses, debugging failures, and moving from "first API call" to "real product feature."

This project bridges that gap with a **structured, developer-first approach** focused on usability, reliability, and — critically — **measuring** whether AI output is actually good.

---

## 🏗️ Project structure

```
ai-support-copilot/
│
├── docs/                          # Developer-facing documentation
│   ├── quickstart.md
│   ├── concepts/prompts.md
│   ├── guides/build-chatbot.md
│   └── troubleshooting/api-errors.md
│
├── src/
│   └── copilot.py                 # Core AI interaction logic
│
├── examples/
│   └── basic_chat.py              # Simple usage example
│
├── evals/
│   └── response_quality.py        # Basic evaluation script
│
├── observability/                 # Evaluation & observability layer
│   ├── evaluator.py               #   measures quality, detects failures
│   ├── reliability.py             #   retry policy + call_with_retries
│   ├── metrics.py                 #   quality-metrics aggregation
│   ├── monitor.py                 #   end-to-end monitor + report()
│   └── README.md
│
├── demo.py                        # Runnable demo (retries + metrics, no API key)
└── tests/
    └── test_observability.py      # 11 passing tests
```

---

## 🔎 Evaluation & Observability Layer

The [`observability/`](observability/) package turns "call the API and hope" into a monitored loop where AI output is measured, not assumed correct.

| Capability | How |
|---|---|
| **Measures response quality** | Scores each response 0–1 across relevance, length adequacy, structure, and hedging; passes/fails against a threshold. |
| **Detects failures** | Hard-fails empty output, error markers, and fallback answers ("I don't know", "I'm not sure"). |
| **Triggers retries** | Re-invokes the model on exceptions *and* low-quality responses with exponential backoff; keeps the best attempt. |
| **Produces quality metrics** | Aggregates pass rate, failure rate, retry rate, mean/min quality score, average attempts, and latency p50/p95. |

### Try it (no API key needed)

```bash
python demo.py
```

```python
from observability import ObservabilityMonitor, ResponseEvaluator, RetryPolicy

monitor = ObservabilityMonitor(
    model,                                   # your src/copilot.py call
    evaluator=ResponseEvaluator(threshold=0.6),
    policy=RetryPolicy(max_retries=3),
)
answer = monitor.handle("How do I reset my password?")
print(monitor.report())
# {'total': 1, 'pass_rate': 1.0, 'failure_rate': 0.0, 'retry_rate': 0.0,
#  'avg_quality_score': 0.86, 'avg_attempts': 1.0, 'latency_ms_p50': ...}
```

### Run the tests

```bash
pip install pytest
pytest -q          # 11 passing tests
```

---

## ⚡ Quickstart

1. Clone the repository
2. Add your API key
3. Run the example: `python examples/basic_chat.py`

See the [Quickstart Guide](docs/quickstart.md) for detailed setup.

---

## 📚 Developer Learning Path

- 👉 [Quickstart](docs/quickstart.md) — run your first AI interaction
- 👉 [Prompt Design](docs/concepts/prompts.md) — structure inputs for better outputs
- 👉 [Build a Chatbot](docs/guides/build-chatbot.md) — step-by-step implementation
- 👉 [API Errors & Troubleshooting](docs/troubleshooting/api-errors.md) — debug real-world issues
- 👉 [`src/copilot.py`](src/copilot.py) — core AI interaction logic
- 👉 [`observability/`](observability/) — measure quality, detect failures, retry, and report metrics

---

## 🧩 Key Concepts Covered

- **Prompt design** — structuring inputs, using context, avoiding common mistakes
- **Response handling** — parsing responses, managing incomplete or irrelevant answers
- **Failure modes** — API errors, hallucinated or low-quality responses
- **Evaluation & observability** — scoring quality, detecting failures, retrying, and producing metrics

---

## 🔮 Future Improvements

- Context-aware responses using external data (RAG)
- Persisting metrics to a dashboard / time-series store
- Streaming responses and latency budgets
- Tool usage and agent-based workflows

---

## 👤 Author

Somesh Chawan
Developer Experience | Technical Writer → Developer Educator
Focused on building developer-first documentation systems, API learning experiences, and AI-assisted workflows.

---

## 📄 License

MIT License
