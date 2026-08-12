import sqlite3

try:
    from src.db import get_connection
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution.
    from db import get_connection


_schema_cache: str | None = None


def get_schema_text() -> str:
    """Return a cached plain-text description of the SQLite database schema."""
    global _schema_cache

    if _schema_cache is not None:
        return _schema_cache

    try:
        with get_connection() as connection:
            tables = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()

            schema_parts: list[str] = []

            for (table_name,) in tables:
                columns = connection.execute(
                    f"PRAGMA table_info('{table_name}')"
                ).fetchall()

                foreign_keys = connection.execute(
                    f"PRAGMA foreign_key_list('{table_name}')"
                ).fetchall()

                lines = [f"TABLE: {table_name}", "COLUMNS:"]

                for column in columns:
                    _, name, data_type, not_null, default, primary_key = column

                    details = f"  - {name} {data_type}"

                    if primary_key:
                        details += " PRIMARY KEY"

                    if not_null:
                        details += " NOT NULL"

                    if default is not None:
                        details += f" DEFAULT {default}"

                    lines.append(details)

                if foreign_keys:
                    lines.append("FOREIGN KEYS:")

                    for foreign_key in foreign_keys:
                        _, _, referenced_table, from_column, to_column, *_ = foreign_key
                        lines.append(
                            f"  - {from_column} REFERENCES {referenced_table}({to_column})"
                        )

                schema_parts.append("\n".join(lines))

            _schema_cache = "\n\n".join(schema_parts)
            return _schema_cache

    except sqlite3.Error as error:
        raise RuntimeError(f"Unable to read database schema: {error}") from error
