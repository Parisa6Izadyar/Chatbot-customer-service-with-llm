"""Regression tests for deterministic demo replies and published ShopSmart policy."""
import json
from src.chat_engine import ChatEngine
from src.paths import DATA_DIR


def _policies():
    return {p["doc_id"]: p["content"] for p in json.loads((DATA_DIR / "company_policies.json").read_text())["policies"]}


def test_cancellation_reply_matches_policy_window():
    engine = ChatEngine()
    engine.llm.mode = "demo"
    result = engine.process_message("I want to cancel my order")
    assert "2 hours" in result["response"]
    assert "2 hours" in _policies()["POL006"]


def test_return_reply_matches_policy_window():
    engine = ChatEngine()
    engine.llm.mode = "demo"
    result = engine.process_message("Can I return my shoes?")
    assert "30 days" in result["response"]
    assert "30 days" in _policies()["POL003"]


def test_refund_reply_matches_policy_window():
    engine = ChatEngine()
    engine.llm.mode = "demo"
    result = engine.process_message("How long does a refund take?")
    assert result["action"] == "ANSWER"
    assert "5 to 7 business days" in result["response"]
    assert "5 to 7 business days" in _policies()["POL004"]
