"""Prompt templates for SQL generation and result explanation."""

from __future__ import annotations

SQL_SYSTEM_PROMPT = """
You are an expert SQLite SQL generator.

Your task is to convert the user's natural-language question into exactly
one valid SQLite SELECT statement.

Rules:
- Output only a single valid SQLite SELECT statement.
- Do not use markdown code fences.
- Do not provide explanations.
- Do not add comments.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, ATTACH, PRAGMA,
  CREATE, or any other statement that modifies the database.
- Use only the exact table names and column names provided in the schema.
- Do not invent tables, columns, relationships, or values.
- The query must be compatible with SQLite.
- If the question cannot be answered using the provided schema, output
  exactly:
-- CANNOT_ANSWER: <short reason>
""".strip()

EXPLAIN_SYSTEM_PROMPT = """
You explain SQL query results to a user in simple language.

Explain the result in 2-3 plain-English sentences.
Briefly describe what the query answered and what the result shows.

Rules:
- Use simple, clear language.
- Do not use unnecessary technical jargon.
- Do not repeat the raw SQL statement verbatim.
- Base the explanation only on the question, SQL, and result provided.
- Do not invent information that is not present in the result.
""".strip()


def build_generation_prompt(
    question: str,
    schema_text: str,
    previous_error: str | None = None,
) -> str:
    """Build the user prompt used to generate or correct SQL."""
    prompt = f"""
Database schema:

{schema_text}

User question:

{question}
""".strip()

    if previous_error is not None:
        previous_sql = previous_error.split("DATABASE ERROR:", 1)[0].strip()
        database_error = previous_error.split("DATABASE ERROR:", 1)[-1].strip()
        prompt += "\n\n" + (
            "The previous SQL attempt failed.\n\n"
            f"Previous SQL:\n{previous_sql}\n\n"
            f"DATABASE ERROR:\n{database_error}\n\n"
            "Fix the specific problem described by the database error.\n"
            "Generate a new valid SQLite SELECT statement that answers the original\n"
            "user question."
        )

    return prompt


def build_explanation_prompt(
    question: str,
    sql: str,
    result_preview: str,
) -> str:
    """Build the prompt used to generate a plain-English result explanation."""
    return f"""
User question:
{question}

SQL query:
{sql}

Query result:
{result_preview}

Explain what this query answered and what the result shows.
""".strip()
