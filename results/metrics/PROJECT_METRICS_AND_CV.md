# Reproducible evaluation and CV evidence (29 October 2026)

## Scope
Evaluation uses **deterministic demo mode**, not a live LLM. The 17 supplied scenarios test **action routing only**, not factual answer correctness or generalization.

- Baseline (original project): **16/17 = 94.1%** action-routing matches.
- Reviewed revision (same 17 cases): **17/17 = 100%** action-routing matches.
- The improvements were developed against the same test set; results are **in-sample regression measurements**, not an independent benchmark.
- The 8 automated tests cover baseline behavior and selected policy-alignment cases.

## CV-ready bullet (after review and publication)
Developed a policy-grounded customer-support chatbot with four-way action routing (ANSWER, CLARIFY, ESCALATE, REFUSE); improved deterministic demo-mode routing from 94.1% to 100% on a 17-case regression set, supported by automated tests.

**Do not claim:** 100% response accuracy, live LLM performance, real-user accuracy, or production deployment.
