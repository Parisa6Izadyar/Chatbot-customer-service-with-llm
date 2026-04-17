import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in {None, ""}:
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.llm_interface import LLMInterface
from src.logger import ChatLogger
from src.input_analyzer import InputAnalyzer
from src.retriever import PolicyRetriever


class ChatEngine:
    """
    Main chatbot orchestration pipeline.
    """

    def __init__(self) -> None:
        self.analyzer = InputAnalyzer()
        self.retriever = PolicyRetriever()
        self.llm = LLMInterface()
        self.logger = ChatLogger()

    def _extract_keywords(self, user_message: str) -> List[str]:
        tokens = re.findall(r"\b[\w']+\b", user_message.lower())
        short_words = {"a", "an", "and", "for", "i", "is", "my", "of", "the", "to", "we"}
        return [token for token in tokens if len(token) > 2 and token not in short_words]

    def _choose_action(self, analysis: Dict[str, Any], understanding: Dict[str, Any]) -> str:
        if analysis.get("is_out_of_scope", False) or understanding.get("out_of_scope", False):
            return "REFUSE"
        if analysis.get("needs_escalation", False) or understanding.get("needs_escalation", False):
            return "ESCALATE"
        if (
            analysis.get("is_ambiguous", False)
            or analysis.get("intent") == "unclear"
            or understanding.get("needs_clarification", False)
        ):
            return "CLARIFY"
        return "ANSWER"

    def process_message(self, user_message: str) -> Dict[str, Any]:
        analysis = self.analyzer.analyze(user_message)
        understanding = self.llm.understand_user_message(user_message)

        resolved_intent = understanding.get("intent") or analysis.get("intent", "unclear")
        if resolved_intent == "unclear":
            resolved_intent = analysis.get("intent", "unclear")

        retrieval_input = {
            "intent": resolved_intent,
            "matched_keywords": analysis.get("matched_keywords", self._extract_keywords(user_message)),
        }

        retrieved_policies = self.retriever.retrieve(retrieval_input)
        retrieved_context = self.retriever.format_context(retrieved_policies)

        action = self._choose_action(analysis, understanding)

        final_reply = self.llm.generate_response(
            user_message=user_message,
            retrieved_context=retrieved_context,
            action=action,
            analysis_reason=understanding.get("reason", ""),
        )

        policy_titles = " | ".join([policy.get("title", "") for policy in retrieved_policies])

        if hasattr(self.llm, "demo_mode"):
            mode = "demo" if self.llm.demo_mode else "llm"
        else:
            mode = getattr(self.llm, "mode", "demo")

        self.logger.log(
            user_message=user_message,
            bot_response=final_reply,
            intent=resolved_intent,
            action=action,
            mode=mode,
        )

        return {
            "response": final_reply,
            "action": action,
            "analysis": analysis,
            "understanding": understanding,
            "retrieved_policies": retrieved_policies,
            "retrieved_context": retrieved_context,
            "policy_titles": policy_titles,
            "llm_mode": mode,
            "llm_mode_reason": getattr(
                self.llm,
                "mode_reason",
                "OPENAI_API_KEY is not set, so the chatbot can only use local demo replies."
            ),
            "llm_understanding_error": "",
            "llm_generation_error": "",
        }

    def chat(self, user_message: str) -> str:
        result = self.process_message(user_message)
        return result["response"]


if __name__ == "__main__":
    engine = ChatEngine()

    print("ShopSmart Chatbot is running.")
    print("Type 'exit' or 'quit' to stop.\n")

    try:
        while True:
            user_message = input("Customer: ").strip()

            if user_message.lower() in {"exit", "quit"}:
                print("Chat ended.")
                break

            if not user_message:
                print("Bot: Please enter a message so I can help.\n")
                continue

            reply = engine.chat(user_message)
            print(f"Bot: {reply}\n")
    except KeyboardInterrupt:
        print("\nChat ended.")