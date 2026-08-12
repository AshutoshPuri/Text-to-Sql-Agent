from pathlib import Path

# Path to the SQLite database, resolved relative to this file so it works from any working directory.
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "ecommerce.db"

# Local Ollama model used to generate and explain SQL.
MODEL_NAME = "qwen2.5-coder:7b"

# Maximum number of automatic retries after a SQL error or safety failure.
MAX_RETRIES = 2
