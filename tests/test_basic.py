from src.chat_engine import ChatEngine
from src.llm_interface import LLMInterface


def test_llm_interface_exposes_generate_response():
    llm = LLMInterface()
    assert hasattr(llm, "generate_response")


def test_chat_engine_returns_a_response_in_demo_mode():
    engine = ChatEngine()
    result = engine.process_message("Where is my order?")

    assert isinstance(result["response"], str)
    assert result["response"].strip() != ""
    assert result["action"] in {"ANSWER", "CLARIFY", "ESCALATE", "REFUSE"}
    assert result["llm_mode"] in {"demo", "llm"}
    assert "llm_mode_reason" in result
