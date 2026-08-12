import sqlite3
from urllib.parse import quote

import pandas as pd

try:
    from src.config import DB_PATH
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution.
    from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Open a read-only SQLite connection to the app database."""
    try:
        database_uri = f"file:{quote(str(DB_PATH))}?mode=ro"
        return sqlite3.connect(database_uri, uri=True)
    except sqlite3.Error as exc:
        raise RuntimeError(f"Unable to open database in read-only mode: {exc}") from exc


def run_query(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return the result as a DataFrame."""
    try:
        with get_connection() as connection:
            return pd.read_sql_query(sql, connection)
    except (sqlite3.Error, pd.errors.DatabaseError) as exc:
        raise RuntimeError(f"SQL query execution failed: {exc}") from exc
