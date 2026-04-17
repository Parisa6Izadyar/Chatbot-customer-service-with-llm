import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in {None, ""}:
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.chat_engine import ChatEngine
from src.paths import DATA_DIR, RESULTS_DIR


class ChatbotEvaluator:
    """
    Simple evaluator for the ShopSmart chatbot.

    It reads evaluation queries from a CSV file, runs each query through the
    chatbot pipeline, saves the detailed results, and prints easy-to-read
    summary metrics.
    """

    def __init__(
        self,
        evaluation_path: str | Path | None = None,
        output_path: str | Path | None = None,
    ) -> None:
        self.evaluation_path = Path(evaluation_path or DATA_DIR / "evaluation_queries.csv")
        self.output_path = Path(
            output_path or RESULTS_DIR / "metrics" / "evaluation_results.csv"
        )
        self.chat_engine = ChatEngine()

    def _load_queries(self) -> List[Dict[str, str]]:
        """Load evaluation queries from CSV."""
        if not self.evaluation_path.exists():
            raise FileNotFoundError(f"Evaluation CSV not found: {self.evaluation_path}")

        with self.evaluation_path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            return list(reader)

    def _write_results(self, rows: List[Dict[str, Any]]) -> None:
        """Save detailed evaluation results to CSV."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "query",
            "expected_behavior",
            "detected_intent",
            "action",
            "matches_expected",
            "retrieved_policy_titles",
            "response",
        ]

        with self.output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _build_summary(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute simple summary metrics for the final report."""
        action_counts = Counter(row["action"] for row in rows)

        return {
            "number_of_queries": len(rows),
            "matches_expected": sum(1 for row in rows if row["matches_expected"] == "yes"),
            "counts_per_action": dict(action_counts),
            "number_of_out_of_scope_cases": action_counts.get("REFUSE", 0),
            "number_of_escalation_cases": action_counts.get("ESCALATE", 0),
        }

    def evaluate(self) -> Dict[str, Any]:
        """
        Run the chatbot on every evaluation query and return summary metrics.
        """
        queries = self._load_queries()
        result_rows: List[Dict[str, Any]] = []

        for item in queries:
            query = item.get("query", "").strip()
            expected_behavior = item.get("expected_action", "").strip()

            result = self.chat_engine.process_message(query)
            detected_intent = result["understanding"].get("intent", "unclear")
            action = result["action"]
            response = result["response"]
            retrieved_titles = " | ".join(
                policy.get("title", "") for policy in result["retrieved_policies"]
            )

            result_rows.append(
                {
                    "query": query,
                    "expected_behavior": expected_behavior,
                    "detected_intent": detected_intent,
                    "action": action,
                    "matches_expected": "yes" if action == expected_behavior else "no",
                    "retrieved_policy_titles": retrieved_titles,
                    "response": response,
                }
            )

        self._write_results(result_rows)
        return self._build_summary(result_rows)


if __name__ == "__main__":
    evaluator = ChatbotEvaluator()
    summary = evaluator.evaluate()

    print(f"Evaluation complete. Results saved to: {evaluator.output_path}")
    print("Summary metrics:")
    print(f"- Number of queries: {summary['number_of_queries']}")
    print(f"- Matches expected behavior: {summary['matches_expected']}")
    print(f"- Counts per action: {summary['counts_per_action']}")
    print(f"- Number of out-of-scope cases: {summary['number_of_out_of_scope_cases']}")
    print(f"- Number of escalation cases: {summary['number_of_escalation_cases']}")
