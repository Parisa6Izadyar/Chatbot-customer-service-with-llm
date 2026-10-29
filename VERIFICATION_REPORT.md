# Test notes

## Commands

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_demo_evaluation.py
```

Tests use a deterministic mode fixture to avoid network calls and API costs. The evaluation script writes `results/metrics/evaluation_results.csv`.

## Previously observed results

The local project revision was previously reported to pass 8 tests and match 17 of 17 expected routing actions. Those results were obtained before the latest GitHub-only edits and **do not verify the current branch**.

The evaluation set is small and was used while developing the routing rules. Its score is an in-sample regression measure, not an estimate of live LLM accuracy or performance on new requests.

## Remaining checks

- Run the commands above against this branch in a clean environment.
- Test the Streamlit interface and Ollama/OpenAI paths separately.
- Review the file changes before merging into `main`.
