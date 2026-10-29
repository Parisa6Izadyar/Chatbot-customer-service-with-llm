import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.chat_engine import ChatEngine


def create_engine() -> ChatEngine | None:
    """
    Create the chatbot engine once and return it.

    If setup fails, the app shows an error instead of crashing.
    """
    if "chat_engine" not in st.session_state:
        try:
            st.session_state.chat_engine = ChatEngine()
            st.session_state.chat_engine_error = ""
        except Exception as exc:
            st.session_state.chat_engine = None
            st.session_state.chat_engine_error = str(exc)

    return st.session_state.chat_engine


def init_session_state() -> None:
    """Prepare the conversation history used by the Streamlit app."""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_message(role: str, content: str) -> None:
    """Store one message in the conversation history."""
    st.session_state.messages.append({"role": role, "content": content})


def render_history() -> None:
    """Display all previous messages in the current session."""
    for message in st.session_state.messages:
        speaker = "Customer" if message["role"] == "user" else "Chatbot"
        st.markdown(f"**{speaker}:** {message['content']}")


def main() -> None:
    st.set_page_config(
        page_title="TrustAware E-commerce Customer Service Chatbot",
        layout="centered",
    )

    st.title("TrustAware E-commerce Customer Service Chatbot")
    st.caption("Policy-based customer support prototype · Demo, OpenAI, or local Ollama mode")

    init_session_state()
    engine = create_engine()

    if engine is None:
        st.error(
            "The chatbot could not start. Please check that the project files are present "
            "and that the configuration files can be loaded."
        )
        if st.session_state.get("chat_engine_error"):
            st.code(st.session_state.chat_engine_error)
        return

    if engine.llm.mode == "llm":
        st.success(engine.llm.mode_reason)
    else:
        st.warning(engine.llm.mode_reason)
        st.caption(
            "Create a local `.env` file from `.env.example` and set `OPENAI_API_KEY` "
            "if you want live LLM responses."
        )

    render_history()

    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input("Customer message")
        submitted = st.form_submit_button("Send")

    if submitted:
        if not user_message.strip():
            st.warning("Please enter a message before sending.")
            return

        add_message("user", user_message)

        try:
            result = engine.process_message(user_message)
            bot_reply = result["response"]
            add_message("assistant", bot_reply)

            if result.get("llm_understanding_error"):
                st.warning(
                    "LLM understanding failed, so the app used local fallback analysis: "
                    f"{result['llm_understanding_error']}"
                )

            if result.get("llm_generation_error"):
                st.warning(
                    "LLM reply generation failed, so the app used a demo fallback response: "
                    f"{result['llm_generation_error']}"
                )

        except Exception as exc:
            st.error(
                "The chatbot could not generate a reply. "
                "If you are using the OpenAI API, check your API key, quota, and network access."
            )
            st.code(str(exc))
            return

        st.rerun()


if __name__ == "__main__":
    main()
