
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

if __package__ in {None, ""}:
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.input_analyzer import InputAnalyzer
from src.paths import CONFIGS_DIR, PROJECT_ROOT

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def _load_dotenv_values(path: Path) -> Dict[str, str]:
    """
    Load simple KEY=VALUE pairs from a local .env file.
    """
    if not path.exists():
        return {}

    values: Dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        values[key] = value

    return values


class LLMInterface:
    """
    Wrapper for:
    1. understanding a user message
    2. generating a grounded customer support reply

    Modes:
    - llm: OpenAI API
    - ollama: local free model
    - demo: deterministic fallback
    """

    def __init__(
        self,
        system_prompt_path: str | Path | None = None,
        model_name: str = "gpt-4o-mini",
        api_key: str | None = None,
    ) -> None:
        dotenv_values = _load_dotenv_values(PROJECT_ROOT / ".env")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or dotenv_values.get("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL") or dotenv_values.get("OPENAI_MODEL") or model_name

        self.last_understanding_error = ""
        self.last_generation_error = ""
        self.system_prompt_path = Path(system_prompt_path or CONFIGS_DIR / "system_prompt.txt")
        self.system_prompt = self._load_system_prompt(self.system_prompt_path)

        self._fallback_analyzer = InputAnalyzer()
        self.client = None

        # Priority:
        # 1) OpenAI if API key exists
        # 2) Local Ollama if installed
        # 3) Demo fallback
        if OpenAI is not None and self.api_key:
            self.mode = "llm"
            self.client = OpenAI(api_key=self.api_key)
            self.mode_reason = f"Live OpenAI mode is ready with model `{self.model_name}`."
        else:
            try:
                response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                if response.status_code == 200:
                    self.mode = "ollama"
                    self.client = None
                    self.mode_reason = "Local Ollama LLM mode is enabled."
                else:
                    self.mode = "demo"
                    self.client = None
                    self.mode_reason = "Could not connect to Ollama. Using demo mode."
            except Exception:
                self.mode = "demo"
                self.client = None
                self.mode_reason = "No API key and Ollama not available. Using demo mode."

    def _load_system_prompt(self, path: Path) -> str:
        """
        Load the system prompt from a robust project-root-safe path.
        """
        if not path.exists():
            raise FileNotFoundError(f"System prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    def _fallback_understanding(
        self,
        user_message: str,
        fallback_analysis: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Return a safe local understanding result.
        """
        analysis = fallback_analysis or self._fallback_analyzer.analyze(user_message)
        return {
            "intent": analysis.get("intent", "unclear"),
            "needs_clarification": analysis.get("is_ambiguous", True),
            "needs_escalation": analysis.get("needs_escalation", False),
            "out_of_scope": analysis.get("is_out_of_scope", False),
            "reason": (
                "Demo mode used deterministic analysis. "
                + analysis.get("reason", "A local fallback was used.")
            ),
        }

    def understand_user_message(
        self,
        user_message: str,
        fallback_analysis: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Understand the user message.
        OpenAI mode uses the model.
        Ollama/demo use the deterministic fallback for now.
        """
        if self.mode != "llm":
            return self._fallback_understanding(user_message, fallback_analysis)

        prompt = f"""
Analyze the following ShopSmart customer-service message.

Return ONLY valid JSON with exactly these fields:
{{
  "intent": "...",
  "needs_clarification": true,
  "needs_escalation": false,
  "out_of_scope": false,
  "reason": "..."
}}

Allowed intents:
- order_status
- shipping_info
- return_request
- refund_request
- cancel_order
- payment_issue
- product_question
- complaint
- speak_to_human
- out_of_scope
- unclear

User message:
{user_message}
"""

        try:
            self.last_understanding_error = ""
            response = self.client.chat.completions.create(
                model=self.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an intent classification engine for a ShopSmart "
                            "e-commerce customer service chatbot."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            raw_text = response.choices[0].message.content.strip()
            parsed = json.loads(raw_text)
        except Exception as exc:
            self.last_understanding_error = str(exc)
            fallback_result = self._fallback_understanding(user_message, fallback_analysis)
            fallback_result["reason"] = (
                "LLM understanding failed and local fallback was used. "
                f"Details: {exc}"
            )
            return fallback_result

        fallback_result = self._fallback_understanding(user_message, fallback_analysis)
        parsed.setdefault("intent", fallback_result["intent"])
        parsed.setdefault("needs_clarification", fallback_result["needs_clarification"])
        parsed.setdefault("needs_escalation", fallback_result["needs_escalation"])
        parsed.setdefault("out_of_scope", fallback_result["out_of_scope"])
        parsed.setdefault("reason", fallback_result["reason"])
        return parsed

    def _generate_demo_response(
        self,
        user_message: str,
        retrieved_context: str,
        action: str,
        analysis_reason: str = "",
        intent: str = "unclear",
    ) -> str:
        """
        Safe fallback response generator for demo mode.
        """
        action = action.upper().strip()

        if action == "ESCALATE":
            return (
                "[Demo mode] This issue should be escalated to a human support agent. "
                f"Reason: {analysis_reason or 'This case may require human review.'}"
            )

        if action == "REFUSE":
            return (
                "[Demo mode] I can only help with ShopSmart customer service topics such as "
                "orders, shipping, returns, refunds, payments, and product support."
            )

        if action == "CLARIFY":
            return (
                "[Demo mode] Could you share a little more detail about your issue "
                "so I can guide you correctly?"
            )

        # Choose deterministic demo replies by resolved intent, not by incidental
        # keywords in concatenated retrieved policy documents.
        intent_replies = {
            "cancel_order": "[Demo mode] Orders may be canceled within 2 hours of placement if shipping preparation has not started. Shipped orders cannot be canceled; please use the return process after delivery.",
            "return_request": "[Demo mode] Most unused items may be returned within 30 days of delivery if they remain in original packaging and resellable condition.",
            "refund_request": "[Demo mode] Approved refunds are usually issued to the original payment method within 5 to 7 business days after the return is received and inspected.",
            "shipping_info": "[Demo mode] Standard shipping usually takes 3 to 5 business days; express shipping takes 1 to 2 business days after payment confirmation.",
            "order_status": "[Demo mode] Please provide your order number and shipping confirmation details to check the tracking information. I cannot access live order status in demo mode.",
            "payment_issue": "[Demo mode] If payment fails, check your card details, billing address, balance, and connection. Temporary holds usually clear within 24 hours.",
        }
        if intent in intent_replies:
            return intent_replies[intent]

        clean_context = retrieved_context.replace("\n", " ").strip()

        if "order number" in clean_context.lower():
            return (
                "[Demo mode] I can help with your order status. "
                "Please share your order number so I can guide you more accurately."
            )

        if "refund" in clean_context.lower():
            return (
                "[Demo mode] According to ShopSmart policy, approved refunds are usually "
                "processed within 5 to 7 business days after the returned item is received "
                "and inspected."
            )

        if "shipping" in clean_context.lower():
            return (
                "[Demo mode] ShopSmart standard shipping usually takes 3 to 5 business days, "
                "and express shipping usually takes 1 to 2 business days."
            )

        return (
            "[Demo mode] Based on ShopSmart policy, I found relevant information for your request. "
            "If you want, please share a bit more detail so I can guide you more precisely."
        )

    def _build_generation_prompt(
        self,
        user_message: str,
        retrieved_context: str,
        action: str,
        analysis_reason: str = "",
    ) -> str:
        """
        Create the user prompt for final response generation.
        """
        return f"""
Generate the final customer-support reply for the following ShopSmart request.

Chosen action: {action.upper().strip()}
Analysis reason: {analysis_reason or "No extra analysis reason provided."}

Relevant company policy context:
{retrieved_context}

Customer message:
{user_message}

Write only the final reply that should be shown to the customer.
"""

    def generate_response(
        self,
        user_message: str,
        retrieved_context: str,
        action: str,
        analysis_reason: str = "",
    ) -> str:
        """
        Generate the final customer-facing reply.
        """
        if self.mode == "demo":
            return self._generate_demo_response(
                user_message=user_message,
                retrieved_context=retrieved_context,
                action=action,
                analysis_reason=analysis_reason,
                intent=intent,
            )

        if self.mode == "ollama":
            prompt = self._build_generation_prompt(
                user_message=user_message,
                retrieved_context=retrieved_context,
                action=action,
                analysis_reason=analysis_reason,
                intent=intent,
            )

            try:
                self.last_generation_error = ""
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
                message = data.get("response", "").strip()
                if message:
                    return message
            except Exception as exc:
                self.last_generation_error = str(exc)
                return self._generate_demo_response(
                    user_message=user_message,
                    retrieved_context=retrieved_context,
                    action=action,
                    analysis_reason=(
                        f"{analysis_reason} Fallback used because Ollama response failed: {exc}"
                    ).strip(),
                    intent=intent,
                )

        prompt = self._build_generation_prompt(
            user_message=user_message,
            retrieved_context=retrieved_context,
            action=action,
            analysis_reason=analysis_reason,
        )

        try:
            self.last_generation_error = ""
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            message = response.choices[0].message.content
            if message and message.strip():
                return message.strip()

        except Exception as exc:
            self.last_generation_error = str(exc)
            return self._generate_demo_response(
                user_message=user_message,
                retrieved_context=retrieved_context,
                action=action,
                analysis_reason=(
                    f"{analysis_reason} Fallback used because OpenAI response failed: {exc}"
                ).strip(),
                intent=intent,
            )

        return self._generate_demo_response(
            user_message=user_message,
            retrieved_context=retrieved_context,
            action=action,
            analysis_reason=analysis_reason,
            intent=intent,
        )


if __name__ == "__main__":
    print("Dependency note: install the OpenAI SDK with `pip install openai`.")
    print("Set the API key with OPENAI_API_KEY in your environment or local .env file.\n")

    llm = LLMInterface()
    test_message = "I was charged twice and I want to speak to a manager."

    print("=" * 60)
    print("UNDERSTANDING STEP")
    understanding = llm.understand_user_message(test_message)
    print(understanding)

    print("\n" + "=" * 60)
    print("RESPONSE GENERATION STEP")
    example_context = """
Document ID: POL008
Title: Billing Escalation Policy
Section: Sensitive Billing Cases
Content: Cases involving duplicate charges, fraud concerns, unauthorized transactions,
or repeated billing errors must be escalated to a human support agent immediately.
"""
    reply = llm.generate_response(
        user_message=test_message,
        retrieved_context=example_context.strip(),
        action="ESCALATE",
        analysis_reason=understanding["reason"],
    )
    print(reply)

