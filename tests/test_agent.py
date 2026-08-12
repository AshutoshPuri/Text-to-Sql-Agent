"""Tests for the SQLite agent orchestration and safety checks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent import is_sql_safe
from db import run_query


def test_is_sql_safe_accepts_select_only() -> None:
    """A simple SELECT statement should be accepted as safe."""
    safe, reason = is_sql_safe("SELECT * FROM customers WHERE country = 'USA';")
    assert safe is True
    assert reason == ""


def test_is_sql_safe_accepts_select_with_subquery() -> None:
    """A SELECT containing a subquery should be accepted."""
    safe, reason = is_sql_safe(
        "SELECT customer_id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE country = 'USA')"
    )
    assert safe is True
    assert reason == ""


def test_is_sql_safe_rejects_drop_statement() -> None:
    """DROP statements should be rejected as unsafe."""
    safe, reason = is_sql_safe("DROP TABLE customers")
    assert safe is False
    assert reason != ""
    assert "DROP" in reason.upper()


def test_is_sql_safe_rejects_delete_statement() -> None:
    """DELETE statements should be rejected as unsafe."""
    safe, reason = is_sql_safe("DELETE FROM customers")
    assert safe is False
    assert reason != ""
    assert "DELETE" in reason.upper()


def test_is_sql_safe_rejects_update_statement() -> None:
    """UPDATE statements should be rejected as unsafe."""
    safe, reason = is_sql_safe("UPDATE customers SET country = 'FR' WHERE id = 1")
    assert safe is False
    assert reason != ""
    assert "UPDATE" in reason.upper()


def test_is_sql_safe_rejects_multiple_statements() -> None:
    """Multiple statements should be rejected."""
    safe, reason = is_sql_safe("SELECT 1; DROP TABLE customers;")
    assert safe is False
    assert "single select statement" in reason.lower()


def test_run_query_returns_customer_count() -> None:
    """The seeded ecommerce database should contain 15 customers."""
    result = run_query("SELECT COUNT(*) AS n FROM customers")
    assert result.iloc[0]["n"] == 15
