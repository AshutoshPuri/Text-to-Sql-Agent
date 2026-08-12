"""Reusable Streamlit UI helpers for the ecommerce assistant."""

from __future__ import annotations

import streamlit as st

# These values must match .streamlit/config.toml if either file changes.
BACKGROUND_COLOR = "#0B1120"
SECONDARY_BACKGROUND_COLOR = "#111827"
PRIMARY_COLOR = "#22CFC2"
TEXT_COLOR = "#E6EDF5"

_CSS_INJECTED = False


def inject_custom_css() -> None:
    """Inject the shared CSS styles used across the application."""
    global _CSS_INJECTED
    if _CSS_INJECTED:
        return

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            background: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
        }}

        .user-bubble {{
            background: {PRIMARY_COLOR};
            color: #06111A;
            padding: 0.75rem 1rem;
            border-radius: 16px 16px 4px 16px;
            margin: 0.75rem 0 0.75rem auto;
            max-width: 80%;
            width: fit-content;
            font-weight: 500;
        }}

        .assistant-bubble {{
            background: {SECONDARY_BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            padding: 0.75rem 1rem;
            border-radius: 16px 16px 16px 4px;
            margin: 0.75rem auto 0.75rem 0;
            max-width: 80%;
            width: fit-content;
        }}

        .card {{
            background: {SECONDARY_BACKGROUND_COLOR};
            border: 1px solid rgba(229, 231, 235, 0.08);
            border-radius: 14px;
            padding: 1rem;
            margin: 0.75rem 0;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
        }}

        .assistant-note {{
            border-left: 3px solid {PRIMARY_COLOR};
            padding: 0.75rem 1rem;
            margin-top: 0.75rem;
            background: rgba(34, 211, 238, 0.06);
            border-radius: 0 10px 10px 0;
        }}

        .badge {{
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            background: rgba(34, 211, 238, 0.12);
            color: {PRIMARY_COLOR};
            border: 1px solid rgba(34, 211, 238, 0.25);
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .error-card {{
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 14px;
            padding: 1rem;
            margin: 0.75rem 0;
        }}

        #MainMenu, footer {{
            visibility: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    _CSS_INJECTED = True


def render_header() -> None:
    """Render the application title, subtitle, and model badge."""
    inject_custom_css()
    st.title("Text-to-SQL Agent")
    st.caption("Ask questions about your e-commerce data in plain English.")
    st.markdown(
        '<span class="badge">Powered by Qwen2.5-Coder · Runs 100% locally</span>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> str | None:
    """Render example questions and return the selected question."""
    with st.sidebar:
        st.header("How it works")
        st.write(
            "1. Ask a question in plain English.\n"
            "2. Qwen generates and validates SQL.\n"
            "3. SQLite runs it and explains the result."
        )

        st.divider()
        st.subheader("Try an example")

        examples = [
            "Which product category has the highest total revenue?",
            "Show me the 5 most recent orders",
            "Which country has the most customers?",
            "Which customer has spent the most money?",
            "What percentage of orders are cancelled?",
        ]

        for index, question in enumerate(examples):
            if st.button(question, use_container_width=True, key=f"example_{index}"):
                return question

    return None


def render_sql_card(sql: str, attempts: int) -> None:
    """Render generated SQL and the number of generation attempts."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Generated SQL")
    st.code(sql, language="sql")

    if attempts == 1:
        st.caption("✓ Generated successfully on the first attempt.")
    else:
        st.caption(f"↻ Self-corrected after {attempts} attempts.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_result_card(df, explanation: str) -> None:
    """Render query results, row count, and plain-English explanation."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Query Result")
    st.metric("Rows returned", len(df))
    st.dataframe(df, use_container_width=True)

    st.markdown(
        f'<div class="assistant-note"><strong>Explanation</strong><br>{explanation}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_error_card(message: str) -> None:
    """Render an application error using the shared visual theme."""
    st.markdown(
        f'<div class="error-card"><strong>Unable to answer the question</strong><br>{message}</div>',
        unsafe_allow_html=True,
    )
