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

The implementation is intentionally simple and beginner-friendly so the logic is easy to inspect, explain, and extend.

## Features

- Streamlit web app for interactive chatbot testing
- Console chatbot for quick local runs
- Deterministic analyzer for intent detection and fallback behavior
- Policy retrieval from local JSON knowledge files
- OpenAI mode, Ollama mode, and demo fallback mode
- CSV logging of chatbot interactions
- Basic evaluation script for sample queries
- VS Code task and PowerShell helper for pushing the project to GitHub

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

## Project Structure

```text
AISystemchatbot/
|-- app.py
|-- README.md
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- configs/
|   |-- escalation_rules.json
|   |-- intents.json
|   `-- system_prompt.txt
|-- data/
|   |-- company_policies.json
|   |-- evaluation_queries.csv
|   `-- logs.csv
|-- results/
|   |-- figures/
|   `-- metrics/
|-- scripts/
|   `-- push_to_github.ps1
|-- src/
|   |-- __init__.py
|   |-- chat_engine.py
|   |-- decision_router.py
|   |-- evaluator.py
|   |-- input_analyzer.py
|   |-- llm_interface.py
|   |-- logger.py
|   |-- paths.py
|   `-- retriever.py
|-- tests/
|   `-- test_basic.py
`-- .vscode/
    `-- tasks.json
```

## Quick Start

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and set your values if you want live OpenAI mode.

Example `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

You can also set the key directly in PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

## Run The Project

### Streamlit Web App

```powershell
streamlit run app.py
```

### Console Chatbot

```powershell
python src\chat_engine.py
```

Type `exit` or `quit` to stop the console chatbot.

### Evaluation Script

```powershell
python src\evaluator.py
```

This writes evaluation results to:

```text
results/metrics/evaluation_results.csv
```

### Basic Tests

Install `pytest` if it is not already available in your environment:

```powershell
pip install pytest
```

Then run:

```powershell
python -m pytest
```

## Example User Queries

- `Where is my order?`
- `How long does standard shipping take?`
- `Can I return these shoes if I never wore them?`
- `When will my refund show on my card?`
- `I was charged twice for one purchase`
- `Connect me to a human agent`
- `What is the weather today?`

## GitHub Push From VS Code

This project includes a helper script at `scripts/push_to_github.ps1` and a VS Code task at `.vscode/tasks.json`.

To push the project from VS Code:

1. Create a new empty GitHub repository.
2. Open this folder in VS Code.
3. Press `Ctrl+Shift+P`.
4. Run `Tasks: Run Task`.
5. Choose `GitHub: Push Project`.
6. Enter:
   - your GitHub repository URL
   - the branch name, usually `main`
   - a commit message
7. If prompted, enter your Git name and email.
8. Sign in to GitHub if VS Code asks for authentication.

The script will:
- initialize Git if needed
- create a commit if there are local changes
- set or update the `origin` remote
- push the project to GitHub

You can also run it manually:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\push_to_github.ps1 `
  -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git" `
  -Branch "main" `
  -CommitMessage "Initial project upload"
```

## Known Limitations

- Retrieval is based on simple keyword overlap rather than embeddings or vector search.
- The system does not connect to a real order, payment, or ticketing backend.
- Automated test coverage is still minimal.
- Multi-turn memory is limited.
- Demo mode is useful for testing but does not match full live model quality.

## Future Improvements

- integrate the deterministic analyzer more deeply into routing decisions
- expand automated tests
- improve retrieval quality with embeddings or semantic search
- add richer evaluation metrics
- support stronger multi-turn clarification handling
- connect the chatbot to a real support backend

## Submission Notes

- No secret API key is stored in the repository.
- `.gitignore` excludes virtual environments, environment files, logs, and caches.
- `data/logs.csv` can be regenerated during use.
- Evaluation output is generated at runtime and does not need to be committed.

## Suggested Demo Flow

If you want to show the project quickly on GitHub or in class:

1. Run the Streamlit app.
2. Ask an in-scope question such as `Where is my order?`
3. Ask an escalation question such as `I was charged twice`
4. Ask an out-of-scope question such as `Tell me a joke`
5. Run the evaluator to show saved results



## Reproducible demo-mode regression results (2026-10-29)

Run `python -m pytest -q` and `python scripts/run_demo_evaluation.py` after installing `requirements.txt`.

On the supplied 17-case evaluation set, action-routing matches improved from **16/17 (94.1%)** in the original baseline to **17/17 (100%)** after regression fixes. The updated test suite has **8 tests**. These are **in-sample deterministic demo-mode regression results**, not live LLM accuracy or generalization estimates. OpenAI/Ollama and Streamlit were not end-to-end tested. See `results/metrics/PROJECT_METRICS_AND_CV.md` for the claim boundaries and `VERIFICATION_REPORT.md` for the local verification report.

Runtime log `data/logs.csv` is ignored and must not be committed. The metrics CSV is intentionally versioned as a small, reproducible example output.
