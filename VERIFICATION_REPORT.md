# Verification report — 2026-10-29

Source: original user-provided ZIP and reviewed local revision.

## Local tests before GitHub publication

```text
8 passed
```

## Demo evaluation

```text
{'number_of_queries': 17, 'matches_expected': 17, 'counts_per_action': {'ANSWER': 8, 'CLARIFY': 2, 'ESCALATE': 4, 'REFUSE': 3}}
```

## Scope and limitations

- Demo mode only; live OpenAI/Ollama and Streamlit UI were not end-to-end tested.
- The 17 cases were reused during bug fixing, so results are in-sample regression measurements.
- Three added tests check selected reply timing limits against policy JSON; this is not comprehensive answer-quality evaluation.
- Runtime logs and local secrets are excluded; `data/logs.csv` is ignored.
- These numbers describe local testing of the reviewed revision, **not** GitHub Actions CI.
- GitHub publication is proposed on a separate review branch; `main` remains unchanged until a PR is approved and merged.
