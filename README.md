# TrustAware E-commerce Customer Service Chatbot

## Project Title
TrustAware E-commerce Customer Service Chatbot is a university project that demonstrates how a large language model can support customer service for a fictional online store called **ShopSmart**.

## Problem Statement
Online stores receive many repetitive support questions about shipping, order tracking, returns, refunds, cancellations, and payment issues. A chatbot can help answer these quickly, but it should not guess, invent policies, or answer unrelated questions.

This project explores a simple trust-aware approach:
- use company policy documents as the main source of truth
- classify customer requests into support intents
- choose whether to answer, clarify, escalate, or refuse
- keep the system easy to understand, test, and explain in a university report

## Originality
This is not just a free-form chatbot. The project focuses on **trust-aware behavior**:
- grounded policy retrieval before answering
- structured action selection: `ANSWER`, `CLARIFY`, `ESCALATE`, `REFUSE`
- out-of-scope refusal for unrelated questions
- escalation for sensitive billing or human-support requests
- logging and evaluation so chatbot behavior can be reviewed later

It is intentionally simple and beginner-friendly rather than highly abstract or production-complex.

## Architecture Overview
The project is split into small modules with clear responsibilities:

1. `LLMInterface` handles message understanding and response generation.
2. `PolicyRetriever` finds the most relevant ShopSmart policy documents.
3. `ChatEngine` orchestrates the chatbot pipeline.
4. `InteractionLogger` stores each chat turn in a CSV log.
5. `ChatbotEvaluator` runs a small evaluation dataset and saves results.
6. `app.py` provides a Streamlit chatbot interface.

### High-level pipeline
1. The user enters a message.
2. The system detects the likely intent and support needs.
3. Relevant policy documents are retrieved.
4. The chatbot chooses an action:
   - `ANSWER`
   - `CLARIFY`
   - `ESCALATE`
   - `REFUSE`
5. A final reply is generated.
6. The conversation turn is logged.

## Project Structure
```text
AISystem7May_backup/
|-- app.py
|-- README.md
|-- requirements.txt
|-- configs/
|   |-- intents.json
|   |-- escalation_rules.json
|   `-- system_prompt.txt
|-- data/
|   |-- company_policies.json
|   |-- evaluation_queries.csv
|   `-- logs.csv
|-- results/
|   |-- figures/
|   `-- metrics/
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
`-- tests/
    `-- test_basic.py
```

## Main Files
- `app.py`: Streamlit web interface for interactive chatting.
- `requirements.txt`: minimal Python dependencies used by the project.
- `configs/intents.json`: supported chatbot intents and example customer requests.
- `configs/escalation_rules.json`: escalation rules for risky or human-required cases.
- `configs/system_prompt.txt`: system instructions used by the LLM.
- `data/company_policies.json`: ShopSmart policy knowledge base.
- `data/evaluation_queries.csv`: sample evaluation queries with expected behavior.
- `data/logs.csv`: interaction log file created during chatbot use.
- `src/paths.py`: project-root-safe folder paths built with `pathlib`.
- `src/input_analyzer.py`: deterministic analyzer used in fallback logic and local testing.
- `src/retriever.py`: policy retrieval logic based on intent and keyword overlap.
- `src/llm_interface.py`: OpenAI integration plus demo fallback when the API is unavailable.
- `src/chat_engine.py`: main orchestration pipeline that combines understanding, retrieval, action selection, response generation, and logging.
- `src/logger.py`: CSV logger for chatbot sessions.
- `src/evaluator.py`: evaluation script that runs the chatbot on sample queries.

## Push To GitHub
This project now includes a helper script at `scripts/push_to_github.ps1` so you can initialize Git, commit your current files, connect the remote, and push with one command.

1. Install **Git for Windows** if `git` is not available in PowerShell.
2. Create an empty GitHub repository.
3. In **VS Code**, press `Ctrl+Shift+P`, run `Tasks: Run Task`, then choose `GitHub: Push Project`.
4. Enter the GitHub repo URL, branch, and commit message when VS Code asks.

You can also run it manually from the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\push_to_github.ps1 `
  -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git" `
  -Branch "main" `
  -CommitMessage "Initial project upload"
```

The script will:
- initialize Git if needed
- stage all current files
- create a commit if there are changes
- ask for your Git name and email the first time if they are not configured
- set or update the `origin` remote
- push to GitHub on the branch you choose

## Setup Instructions
### 1. Create a virtual environment
Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

## API Key Setup
This project supports two modes:

- `llm` mode: uses the OpenAI API
- `demo` mode: uses local fallback behavior when the API is unavailable

To enable live LLM execution in PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Important notes:
- Do not put secret keys directly in the code.
- Do not commit `.env` files or private keys.
- Live OpenAI execution may require active API billing and available quota.
- If the key is missing, invalid, or quota is exceeded, the project may fall back to demo behavior.

## How to Run the Console Chatbot
From the project root:

```powershell
python src\chat_engine.py
```

Type `exit` or `quit` to stop the conversation.

## How to Run the Streamlit App
From the project root:

```powershell
streamlit run app.py
```

The app keeps conversation history in session state and shows a small prototype note.

## How to Run the Evaluator
From the project root:

```powershell
python src\evaluator.py
```

This creates:
- `results/metrics/evaluation_results.csv`

The evaluator prints a short summary in the terminal and saves row-by-row outputs for later review.

## Sample User Queries
- `Where is my order?`
- `How long does standard shipping take?`
- `Can I return these shoes if I never wore them?`
- `When will my refund show on my card?`
- `I was charged twice for one purchase`
- `Connect me to a human agent`
- `What is the weather today?`

## Known Limitations
- The current runtime flow relies mainly on the LLM interface rather than fully routing through the deterministic analyzer in all cases.
- Demo mode is useful for local testing, but it does not represent full live LLM quality.
- The project uses simple keyword-based retrieval instead of embeddings or vector search.
- There is no real order database or transaction backend.
- Product answers are limited to whatever information appears in the supplied context.
- Automated tests are still minimal.

## Future Improvements
- Integrate `InputAnalyzer` directly into the main chat pipeline.
- Add stronger unit tests for retrieval, logging, evaluation, and routing.
- Improve intent classification and ambiguity handling.
- Add richer evaluation metrics such as per-intent accuracy.
- Support multi-turn memory and clarification tracking.
- Connect to a real backend for order lookup or support escalation.

## Submission Readiness Notes
- No secret API key is stored in the repository.
- Generated cache files, logs, `.env`, and virtual environments are ignored by `.gitignore`.
- `data/logs.csv` starts with headers only, so professors can generate their own logs.
- Evaluation output is generated when the evaluator runs and is not required to be committed.

## What a Professor Should Test First
If a professor wants to verify the project quickly, these are the best first checks:

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. Run the console chatbot:
```powershell
python src\chat_engine.py
```

3. Try these test questions:
- `Where is my order?`
- `I was charged twice`
- `Connect me to a human agent`
- `Tell me a joke`

4. Run the evaluator:
```powershell
python src\evaluator.py
```

5. If Streamlit is installed, run the web app:
```powershell
streamlit run app.py
```
