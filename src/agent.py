"""Core text-to-SQL agent orchestration for the local app."""

from __future__ import annotations

import re

import ollama

try:
    from src.config import MAX_RETRIES, MODEL_NAME
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution.
    from config import MAX_RETRIES, MODEL_NAME

try:
    from src.db import run_query
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution.
    from db import run_query

try:
    from src.prompts import EXPLAIN_SYSTEM_PROMPT, SQL_SYSTEM_PROMPT, build_explanation_prompt, build_generation_prompt
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution.
    from prompts import EXPLAIN_SYSTEM_PROMPT, SQL_SYSTEM_PROMPT, build_explanation_prompt, build_generation_prompt

try:
    from src.schema import get_schema_text
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution.
    from schema import get_schema_text


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the local Ollama model and return the message content as plain text."""
    print(f"[agent] calling Ollama model={MODEL_NAME}")
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:  # pragma: no cover - depends on local service availability.
        raise RuntimeError("Ollama is unreachable. Please check that `ollama serve` is running.") from exc

    message = response.message if hasattr(response, "message") else response["message"]
    content = message.content if hasattr(message, "content") else message["content"]
    text = str(content).strip()
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\s*```$", "", text, flags=re.DOTALL)
    return text.strip()


def is_sql_safe(sql: str) -> tuple[bool, str]:
    """Return whether a SQL string is a single safe SQLite SELECT statement."""
    text = sql.strip()
    if not text:
        return False, "SQL is empty."
    if text.endswith(";"):
        text = text[:-1].rstrip()
    if ";" in text:
        return False, "SQL must be a single SELECT statement."
    upper = text.upper()
    disallowed = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "ATTACH", "PRAGMA", "CREATE"]
    for keyword in disallowed:
        if re.search(rf"\b{keyword}\b", upper):
            return False, f"Unsafe SQL detected: contains {keyword}."
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False, "SQL must be a single SELECT statement."
    return True, ""


def generate_sql(question: str, previous_error: str | None = None) -> str:
    """Generate SQL from a question using the schema and retry feedback if provided."""
    print(f"[agent] generating SQL for: {question}")
    prompt = build_generation_prompt(question, get_schema_text(), previous_error)
    sql = call_llm(SQL_SYSTEM_PROMPT, prompt)
    cleaned = sql.strip()
    if cleaned.startswith("-- CANNOT_ANSWER"):
        raise ValueError(cleaned)
    print(f"[agent] generated SQL: {cleaned}")
    return cleaned


def explain_result(question: str, sql: str, df) -> str:
    """Ask the model to explain the query result in plain English."""
    preview = df.head(5).to_string(index=False)
    preview_text = f"Rows returned: {len(df)}\n{preview}"
    prompt = build_explanation_prompt(question, sql, preview_text)
    explanation = call_llm(EXPLAIN_SYSTEM_PROMPT, prompt)
    print(f"[agent] explanation generated: {explanation[:120]}")
    return explanation


def answer_question(question: str) -> dict:
    """Run the SQL-generation and execution loop with retries and final error reporting."""
    attempts = 0
    last_sql = ""
    last_error = ""
    previous_error: str | None = None

    for attempt in range(1, MAX_RETRIES + 2):
        attempts = attempt
        print(f"[agent] attempt {attempt}/{MAX_RETRIES + 1} for question: {question}")
        try:
            sql = generate_sql(question, previous_error)
            last_sql = sql
            safe, reason = is_sql_safe(sql)
            if not safe:
                print(f"[agent] SQL rejected by safety check: {reason}")
                last_error = reason
                if attempt <= MAX_RETRIES:
                    previous_error = reason
                    print(f"[agent] retrying after unsafe SQL: {attempt + 1}/{MAX_RETRIES + 1}")
                    continue
                raise RuntimeError(f"SQL generation or execution failed after {attempts} attempts. Last SQL: {last_sql}. Last error: {last_error}")

            result = run_query(sql)
            print(f"[agent] query executed successfully with {len(result)} rows")
            explanation = explain_result(question, sql, result)
            return {"sql": sql, "result": result, "explanation": explanation, "attempts": attempts}
        except ValueError as exc:
            message = str(exc)
            if message.startswith("-- CANNOT_ANSWER"):
                print(f"[agent] model answered with inability: {message}")
                raise
            last_error = message
            print(f"[agent] generation error: {message}")
        except Exception as exc:
            message = str(exc)
            last_error = message
            print(f"[agent] execution error: {message}")

        if attempt <= MAX_RETRIES:
            previous_error = message
            print(f"[agent] retrying after error: {attempt + 1}/{MAX_RETRIES + 1}")
            continue

        raise RuntimeError(f"SQL generation or execution failed after {attempts} attempts. Last SQL: {last_sql}. Last error: {last_error}")

    raise RuntimeError(f"SQL generation or execution failed after {attempts} attempts. Last SQL: {last_sql}. Last error: {last_error}")
