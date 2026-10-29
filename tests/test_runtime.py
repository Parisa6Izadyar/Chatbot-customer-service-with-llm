from unittest.mock import patch

from src.chat_engine import ChatEngine
from src.llm_interface import LLMInterface


def test_explicit_demo_mode_avoids_external_services(monkeypatch):
    monkeypatch.setenv("CHATBOT_MODE", "demo")
    with patch("src.llm_interface.requests.get", side_effect=AssertionError("Unexpected network call")):
        with patch("src.llm_interface.OpenAI", side_effect=AssertionError("Unexpected API client")):
            engine = ChatEngine()
    assert engine.llm.mode == "demo"


def test_invalid_runtime_mode_is_rejected(monkeypatch):
    monkeypatch.setenv("CHATBOT_MODE", "invalid")
    with patch("src.llm_interface.LLMInterface.__init__", wraps=LLMInterface.__init__):
        pass
