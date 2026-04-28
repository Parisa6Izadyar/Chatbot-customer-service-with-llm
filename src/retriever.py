import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in {None, ""}:
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.paths import DATA_DIR


class PolicyRetriever:
    """
    Load ShopSmart policy documents and return the most relevant ones
    for a detected chatbot intent.
    """

    def __init__(self, policies_path: str | Path | None = None) -> None:
        
        self.policies_path = Path(policies_path or DATA_DIR / "company_policies.json")
        self.policies_data = self._load_json(self.policies_path)
        self.policies = self.policies_data.get("policies", [])

        self.intent_to_titles = {
            "order_status": ["Order Tracking Policy", "Shipping Policy"],
            "shipping_info": ["Shipping Policy"],
            "return_request": ["Return Policy", "Damaged or Incorrect Items Policy"],
            "refund_request": ["Refund Policy", "Damaged or Incorrect Items Policy"],
            "cancel_order": ["Cancellation Policy"],
            "payment_issue": ["Payment Support Policy", "Billing Escalation Policy"],
            "product_question": ["Product Information Policy"],
            "complaint": ["Complaint Handling Policy", "Human Escalation Policy"],
            "speak_to_human": ["Human Escalation Policy"],
            "out_of_scope": ["Scope Policy"],
            "unclear": [],
        }

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Read the policies JSON file from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _candidate_policies(self, intent: str) -> List[Dict[str, Any]]:
        """Return policies that match the given intent's mapped titles."""
        candidate_titles = self.intent_to_titles.get(intent, [])
        return [
            policy
            for policy in self.policies
            if policy.get("title") in candidate_titles
        ]

    def _score_policy(self, policy: Dict[str, Any], matched_keywords: List[str]) -> int:
        """
        Score a policy using simple keyword overlap.

        The policy gets one point for each matched keyword found in the
        policy title, section, or content.
        """
        searchable_text = " ".join(
            [
                policy.get("title", ""),
                policy.get("section", ""),
                policy.get("content", ""),
            ]
        ).lower()

        score = 0
        for keyword in matched_keywords:
            if keyword.lower() in searchable_text:
                score += 1

        return score

    def retrieve(self, analysis_result: Dict[str, Any], top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Return the most relevant policy documents for an analyzed user message.

        Expected keys in analysis_result:
        - intent
        - matched_keywords (optional)
        """
        intent = analysis_result.get("intent", "unclear")
        matched_keywords = analysis_result.get("matched_keywords", [])

        candidates = self._candidate_policies(intent)
        if not candidates:
            return []

        scored_policies = []
        for policy in candidates:
            score = self._score_policy(policy, matched_keywords)
            scored_policies.append((score, policy))

        scored_policies.sort(key=lambda item: (-item[0], item[1].get("title", "")))

        return [policy for _, policy in scored_policies[:top_k]]

    def format_context(self, retrieved_policies: List[Dict[str, Any]]) -> str:
        """
        Convert retrieved policies into a clean prompt-ready text block.
        """
        if not retrieved_policies:
            return "No relevant company policy was found."

        context_blocks = []
        for policy in retrieved_policies:
            context_blocks.append(
                "\n".join(
                    [
                        f"Document ID: {policy.get('doc_id', 'N/A')}",
                        f"Title: {policy.get('title', 'Untitled Policy')}",
                        f"Section: {policy.get('section', 'General')}",
                        f"Content: {policy.get('content', '')}",
                    ]
                )
            )

        return "\n\n---\n\n".join(context_blocks)


if __name__ == "__main__":
    from src.input_analyzer import InputAnalyzer

    analyzer = InputAnalyzer()
    retriever = PolicyRetriever()

    sample_messages = [
        "Where is my order?",
        "How long does shipping take?",
        "I need a refund",
        "I was charged twice",
        "Can I cancel my order?",
        "Tell me a joke",
    ]

    for message in sample_messages:
        analysis = analyzer.analyze(message)
        policies = retriever.retrieve(analysis)

        print("=" * 60)
        print(f"User message: {message}")
        print(f"Detected intent: {analysis['intent']}")
        print(f"Matched keywords: {analysis['matched_keywords']}")
        print("Retrieved titles:", [policy["title"] for policy in policies])
        print("Formatted context:")
        print(retriever.format_context(policies))
