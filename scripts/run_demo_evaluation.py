"""Run deterministic evaluation regardless of local OpenAI/Ollama availability."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.evaluator import ChatbotEvaluator

if __name__ == "__main__":
    evaluator = ChatbotEvaluator()
    evaluator.chat_engine.llm.mode = "demo"
    evaluator.chat_engine.llm.client = None
    summary = evaluator.evaluate()
    print(summary)
