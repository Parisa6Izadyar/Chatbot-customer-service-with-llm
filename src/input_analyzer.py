import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set
import sys

if __package__ in {None, ""}:
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.paths import CONFIGS_DIR


class InputAnalyzer:
    """
    Deterministic input analyzer used for local demo mode and policy retrieval.
    """

    STOPWORDS: Set[str] = {
        "a",
        "about",
        "an",
        "and",
        "are",
        "can",
        "do",
        "for",
        "how",
        "i",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "please",
        "the",
        "this",
        "to",
        "what",
        "when",
        "where",
        "was",
        "why",
        "with",
        "you",
        "your",
    }

    def __init__(
        self,
        intents_path: str | Path | None = None,
        escalation_rules_path: str | Path | None = None,
    ):
        self.intents_path = Path(intents_path or CONFIGS_DIR / "intents.json")
        self.escalation_rules_path = Path(
            escalation_rules_path or CONFIGS_DIR / "escalation_rules.json"
        )

        self.intents_data = self._load_json(self.intents_path)
        self.escalation_data = self._load_json(self.escalation_rules_path)

        self.intent_keywords = self._build_intent_keywords()
        self.escalation_keywords = self._extract_escalation_keywords()

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def _keyword_tokens(self, text: str) -> List[str]:
        return [
            token
            for token in self._normalize_text(text).split()
            if token and token not in self.STOPWORDS
        ]

    def _build_intent_keywords(self) -> Dict[str, List[str]]:
        """
        Build keyword lists from intent examples.
        """
        intent_keywords = {}

        for intent_item in self.intents_data.get("intents", []):
            intent_name = intent_item["name"]
            examples = intent_item.get("examples", [])

            keywords: List[str] = []
            for example in examples:
                keywords.extend(self._keyword_tokens(example))

            intent_keywords[intent_name] = sorted(set(keywords))

        return intent_keywords

    def _extract_escalation_keywords(self) -> List[str]:
        """
        Extract escalation keywords from escalation rules.
        """
        keywords = []
        for rule in self.escalation_data.get("rules", []):
            if rule.get("type") == "keyword":
                keywords.append(rule.get("value", "").lower())
        return keywords

    def _detect_intent(self, user_text: str) -> Dict[str, Any]:
        """
        Detect intent using keyword overlap with examples.
        """
        user_words = set(self._keyword_tokens(user_text))

        best_intent = "unclear"
        best_score = 0
        matched_keywords: List[str] = []

        for intent_name, keywords in self.intent_keywords.items():
            overlap = user_words.intersection(set(keywords))
            score = len(overlap)

            if score > best_score:
                best_score = score
                best_intent = intent_name
                matched_keywords = list(overlap)

        if best_score == 0:
            confidence = 0.2
        else:
            confidence = min(0.35 + best_score * 0.18, 0.95)

        return {
            "intent": best_intent,
            "confidence": round(confidence, 2),
            "matched_keywords": matched_keywords
        }

    def _detect_ambiguity(self, user_text: str, intent: str) -> bool:
        """
        Detect whether the input is vague or too short.
        """
        normalized_text = self._normalize_text(user_text)
        word_count = len(normalized_text.split())

        vague_phrases = {
            "help me",
            "i need help",
            "problem",
            "i have a problem",
            "something is wrong",
            "support",
            "help"
        }

        if normalized_text in vague_phrases:
            return True

        if word_count <= 2 and intent == "unclear":
            return True

        if intent == "unclear" and word_count <= 6:
            return True

        return False

    def _detect_out_of_scope(self, intent: str) -> bool:
        return intent == "out_of_scope"

    def _detect_escalation(self, user_text: str, intent: str, confidence: float) -> Dict[str, Any]:
        """
        Detect whether the message should be escalated.
        """
        normalized_text = self._normalize_text(user_text)

        matched_escalation_keywords = []
        for keyword in self.escalation_keywords:
            if keyword in normalized_text:
                matched_escalation_keywords.append(keyword)

        needs_escalation = False
        escalation_reason = None

        if intent == "speak_to_human":
            needs_escalation = True
            escalation_reason = "User explicitly requested a human agent."

        elif matched_escalation_keywords:
            needs_escalation = True
            escalation_reason = f"Matched escalation keywords: {matched_escalation_keywords}"

        elif confidence < 0.45 and intent not in ["unclear", "out_of_scope"]:
            needs_escalation = True
            escalation_reason = "Low confidence in intent detection."

        return {
            "needs_escalation": needs_escalation,
            "escalation_reason": escalation_reason,
            "matched_escalation_keywords": matched_escalation_keywords
        }

    def analyze(self, user_text: str) -> Dict[str, Any]:
        """
        Main analysis function.
        """
        intent_result = self._detect_intent(user_text)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        is_ambiguous = self._detect_ambiguity(user_text, intent)
        is_out_of_scope = self._detect_out_of_scope(intent)
        escalation_result = self._detect_escalation(user_text, intent, confidence)

        if is_out_of_scope:
            reason = "The request is outside supported e-commerce customer service topics."
        elif is_ambiguous:
            reason = "The request is too vague and needs clarification."
        elif escalation_result["needs_escalation"]:
            reason = escalation_result["escalation_reason"] or "The issue should be escalated."
        elif intent == "unclear":
            reason = "The request could not be classified with enough confidence."
        else:
            reason = "The request appears to be in scope and can be answered."

        return {
            "user_text": user_text,
            "intent": intent,
            "confidence": confidence,
            "matched_keywords": intent_result["matched_keywords"],
            "is_ambiguous": is_ambiguous,
            "is_out_of_scope": is_out_of_scope,
            "needs_escalation": escalation_result["needs_escalation"],
            "escalation_reason": escalation_result["escalation_reason"],
            "matched_escalation_keywords": escalation_result["matched_escalation_keywords"],
            "reason": reason,
        }


if __name__ == "__main__":
    analyzer = InputAnalyzer()

    test_inputs = [
        "Where is my order?",
        "I want a refund",
        "Tell me a joke",
        "I need help",
        "I was charged twice",
        "I want to speak to a human"
    ]

    for text in test_inputs:
        print("\nUser Input:", text)
        print(analyzer.analyze(text))
