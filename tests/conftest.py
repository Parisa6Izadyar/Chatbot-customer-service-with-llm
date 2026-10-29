import pytest
from src.llm_interface import LLMInterface


@pytest.fixture(autouse=True)
def demo_mode(monkeypatch):
    def use_demo(self, *args, **kwargs):
        self.mode = "demo"
        self.client = None
        self.mode_reason = "Deterministic test mode."
        self.last_understanding_error = ""
        self.last_generation_error = ""
        self.system_prompt = ""
        from src.input_analyzer import InputAnalyzer
        self._fallback_analyzer = InputAnalyzer()

    monkeypatch.setattr(LLMInterface, "__init__", use_demo)
