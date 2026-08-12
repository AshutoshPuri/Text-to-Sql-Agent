"""Streamlit app entry point for the ecommerce text-to-SQL agent."""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

import streamlit as st

# Ensure src imports work when running from the project root:
#   streamlit run src/app.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

try:
    from src import ui_components
except ModuleNotFoundError:  # pragma: no cover
    from src import ui_components


def _add_question_to_history(question: str) -> int:
    if "history" not in st.session_state:
        st.session_state.history = []

    entry = {
        "question": question,
        "status": "pending",
    }
    st.session_state.history.append(entry)
    return len(st.session_state.history) - 1


def _run_agent_with_status(index: int) -> None:
    status = st.status("Starting text-to-SQL generation...", expanded=True)
    original_print = builtins.print

    def _status_print(*args, sep=" ", end="\n", **kwargs):
        text = sep.join(str(arg) for arg in args)
        if text.startswith("[agent]"):
            stage_text = text.replace("[agent]", "").strip()
            status.markdown(f"**{stage_text}**")
        original_print(*args, sep=sep, end=end, **kwargs)

    builtins.print = _status_print
    try:
        try:
            from src import agent
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Agent dependencies are missing. Install ollama and ensure the local model is available."
            ) from exc

        with st.spinner("Answering your question..."):
            response = agent.answer_question(st.session_state.history[index]["question"])
    except Exception as exc:
        st.session_state.history[index].update({"status": "error", "error": str(exc)})
        status.markdown("**Request failed.**")
    else:
        st.session_state.history[index].update({"status": "done", **response})
        status.markdown("**Answer ready.**")
    finally:
        builtins.print = original_print
        status.empty()


def main() -> None:
    st.set_page_config(
        page_title="Text-to-SQL Agent",
        page_icon=" ",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    ui_components.inject_custom_css()
    ui_components.render_header()

    example_question = ui_components.render_sidebar()
    if example_question:
        user_input = example_question
    else:
        user_input = st.chat_input("Ask a question about your e-commerce data...")

    if user_input:
        question_text = user_input.strip()
        if question_text:
            question_index = _add_question_to_history(question_text)
            _run_agent_with_status(question_index)

    if "history" in st.session_state:
        for exchange in st.session_state.history:
            st.markdown(
                f'<div class="user-bubble">{exchange["question"]}</div>',
                unsafe_allow_html=True,
            )

            if exchange["status"] == "done":
                ui_components.render_sql_card(exchange["sql"], exchange["attempts"])
                ui_components.render_result_card(exchange["result"], exchange["explanation"])
            elif exchange["status"] == "error":
                ui_components.render_error_card(exchange["error"])
            else:
                st.info("Awaiting answer...")


if __name__ == "__main__":
    main()
