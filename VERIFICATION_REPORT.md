# Verification notes

## Reproduce

```bash
CHATBOT_MODE=demo python -m pytest -q
CHATBOT_MODE=demo python scripts/run_demo_evaluation.py
```

## Results

The reviewed local revision passed **10/10 tests** and matched **17/17 expected routing actions** in deterministic demo mode. The tests include two subprocess checks of runtime mode selection. GitHub Actions must also complete on the latest commit before merging.

The 17 cases were used while adjusting the routing logic; the result is an **in-sample regression measure**, not independent model validation. The tests do not establish response factuality across unseen inputs or end-to-end reliability of OpenAI, Ollama, or the Streamlit interface.

Runtime logs are excluded from version control. Use synthetic messages when demonstrating the app.
