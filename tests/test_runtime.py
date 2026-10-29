import os
import subprocess
import sys


def _run_engine(mode):
    env = os.environ.copy()
    env["CHATBOT_MODE"] = mode
    env.pop("OPENAI_API_KEY", None)
    return subprocess.run(
        [sys.executable, "-c", "from src.chat_engine import ChatEngine; print(ChatEngine().llm.mode)"],
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )


def test_explicit_demo_mode():
    result = _run_engine("demo")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "demo"


def test_invalid_runtime_mode_is_rejected():
    result = _run_engine("invalid")
    assert result.returncode != 0
    assert "CHATBOT_MODE must be" in result.stderr
