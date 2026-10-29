from src.chat_engine import ChatEngine

def test_vague_help_requests_clarification():
    result = ChatEngine().process_message("Help me")
    assert result["action"] == "CLARIFY"

def test_cancellation_uses_cancellation_policy():
    result = ChatEngine().process_message("I want to cancel my order")
    assert result["action"] == "ANSWER"
    if result["llm_mode"] == "demo":
        assert "canceled within 2 hours" in result["response"]

def test_return_does_not_answer_refund_timing():
    result = ChatEngine().process_message("Can I return my shoes?")
    if result["llm_mode"] == "demo" and result["action"] == "ANSWER":
        assert "30 days" in result["response"]
