# TrustAware E-commerce Customer Service Chatbot

A trust-aware customer support chatbot for a fictional online store called **ShopSmart**.

This university project explores how an LLM-backed assistant can answer common e-commerce questions while staying grounded in company policy, refusing unrelated requests, and escalating higher-risk cases when needed.

## Overview

The chatbot is designed for customer-service scenarios such as:
- order status
- shipping questions
- returns and refunds
- cancellation requests
- payment issues
- requests to speak to a human agent

Instead of acting like a general free-form assistant, the system follows a safer support workflow:
- retrieve relevant company policy before replying
- classify the user request into a support intent
- choose one of four actions: `ANSWER`, `CLARIFY`, `ESCALATE`, or `REFUSE`
- log interactions for later review
- evaluate behavior on a small test dataset

## Why This Project Is Different

This is not just a chatbot wrapper around an API. The main focus is **trust-aware behavior**:
- policy-grounded answers rather than unsupported guessing
- structured decision-making before response generation
- escalation for risky billing or human-support cases
- refusal for out-of-scope requests
- local fallback behavior when live LLM access is unavailable

The rule-based retrieval and routing logic is kept explicit for reproducible testing.

## Features

- Streamlit web app for interactive chatbot testing
- Console chatbot for quick local runs
- Deterministic analyzer for intent detection and fallback behavior
- Policy retrieval from local JSON knowledge files
- OpenAI mode, Ollama mode, and demo fallback mode
- CSV logging of chatbot interactions
- Basic evaluation script for sample queries

## How It Works

### Pipeline

1. The user sends a message.
2. The system analyzes the message for intent, ambiguity, escalation, and scope.
3. Relevant ShopSmart policy documents are retrieved.
4. The chatbot selects an action:
   - `ANSWER`
   - `CLARIFY`
   - `ESCALATE`
   - `REFUSE`
5. A final reply is generated.
6. The interaction is logged.

### Main Components

- `src/chat_engine.py`: orchestrates the end-to-end chatbot flow
- `src/input_analyzer.py`: deterministic input analysis and fallback logic
- `src/retriever.py`: retrieves relevant policy entries
- `src/llm_interface.py`: handles OpenAI, Ollama, and demo response generation
- `src/logger.py`: stores interactions in CSV format
- `src/evaluator.py`: runs the chatbot against evaluation queries
- `app.py`: Streamlit interface for the chatbot

## Runtime Modes

The project supports three modes:

- `llm`: uses the OpenAI API when `OPENAI_API_KEY` is available
- `ollama`: uses a local Ollama model when OpenAI is not configured but Ollama is running
- `demo`: uses deterministic fallback behavior when no live model is available

This makes the project easier to demo even without paid API access.

## Run in GitHub Codespaces (no local setup)

1. Open this repository on GitHub and select **Code → Codespaces → Create codespace**.
2. In the Codespaces terminal, run:

```bash
CHATBOT_MODE=demo python -m streamlit run app.py --server.address 0.0.0.0
```

3. Open the forwarded **port 8501** from the **Ports** tab. No API key, Ollama installation, or local Python setup is needed for demo mode. Stop the server with `Ctrl+C` when finished. Codespaces may incur usage charges depending on your GitHub plan and allowances.

## Local quick start

Requires Python 3.11 or later.

```bash
python -m pip install -r requirements.txt
```

For an offline demonstration, set `CHATBOT_MODE=demo` in your environment, then run:

```bash
python -m streamlit run app.py
```

For an interactive terminal session:

```bash
python -m src.chat_engine
```

To run the tests and action-routing evaluation:

```bash
python -m pytest -q
python scripts/run_demo_evaluation.py
```

The evaluation writes `results/metrics/evaluation_results.csv`. A successful run should report 17 matching actions on the supplied 17 examples. These are regression cases, not an independent test set.

### Optional live models

To use the OpenAI API, set `OPENAI_API_KEY` in your environment or a local `.env` file (never commit credentials), and leave `CHATBOT_MODE` unset. If no OpenAI key is present, the app attempts a local Ollama connection before falling back to demo mode. Live modes require additional setup and are not covered by the deterministic CI checks.

## Main components

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit chat interface |
| `src/chat_engine.py` | Message processing and four-way action routing |
| `src/input_analyzer.py` | Keyword-based intent and escalation analysis |
| `src/retriever.py` | Policy lookup from local JSON documents |
| `src/llm_interface.py` | Demo responses and optional model integration |
| `src/evaluator.py` | Evaluation of routing decisions |
| `tests/` | Automated regression and policy-alignment checks |

## Evaluation and limitations

- The original baseline matched **16/17 (94.1%)** expected actions; the revised deterministic demo matched **17/17 (100%)** on the same examples. This is **in-sample routing agreement**, not response accuracy, real-world model accuracy, or generalization.
- Keyword retrieval is intentionally simple; no embeddings or vector database are used.
- There is no live order-management, payment, or ticketing integration.
- Streamlit and OpenAI/Ollama are not end-to-end validated by the CI workflow.
- Local interaction logs may contain user-entered text. Use synthetic examples, avoid personal information, and do not commit runtime logs.

See `results/metrics/PROJECT_METRICS_AND_CV.md` for the metric definitions and `VERIFICATION_REPORT.md` for test notes.

## Example user queries

- `Where is my order?`
- `How long does standard shipping take?`
- `Can I return these shoes if I never wore them?`
- `When will my refund show on my card?`
- `I was charged twice for one purchase`
- `Connect me to a human agent`
- `What is the weather today?`

