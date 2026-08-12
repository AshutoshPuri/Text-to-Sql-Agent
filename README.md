
# Text-to-SQL Agent

A local, zero-cost Streamlit text-to-SQL agent built on SQLite and Ollama.
This project converts plain-English questions into safe SQL, executes them against
an e-commerce SQLite database, and returns both results and a natural-language explanation.

## Project Structure

- `data/seed_db.py` - creates and seeds `data/ecommerce.db` with realistic sample data.
- `src/config.py` - configuration constants, including the database path and Ollama model name.
- `src/db.py` - read-only SQLite query execution using Pandas.
- `src/schema.py` - database schema introspection and formatting.
- `src/prompts.py` - prompt templates for SQL generation and explanation.
- `src/agent.py` - core agent logic, safety validation, retry behavior, and result assembly.
- `src/app.py` - Streamlit UI entry point.
- `tests/test_agent.py` - deterministic tests for SQL safety and DB access.

## Prerequisites

- Python 3.11+ / Anaconda Python 3.13 is supported.
- `ollama` CLI installed and available in your PATH.
- A local Ollama model available for use by the agent.

## Setup

```bash
cd /Users/user/Desktop/text-to-sql-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Seed the Database

Run this once before using the app:

```bash
python3 data/seed_db.py
```

This creates `data/ecommerce.db` and inserts:
- 15 customers
- 10 products
- 30 orders
- multiple order items

## Ollama Model Setup

The project is configured to use `qwen2.5-coder:7b` by default.
If that model is not installed locally, pull it first:

```bash
ollama pull qwen2.5-coder:7b
```

Then start the Ollama server:

```bash
ollama serve
```

If the default port is already in use, stop the existing Ollama process first:

```bash
pkill -f "ollama serve"
ollama serve
```

## Run the Streamlit App

Open a new terminal and run:

```bash
cd /Users/user/Desktop/text-to-sql-agent
streamlit run src/app.py
```

Then open the URL printed by Streamlit in your browser.

## What the App Does

The UI lets you enter a plain-English question about the e-commerce database.
On submit, the agent returns:

1. Question
2. Generated SQL
3. Result table
4. Explanation
5. Attempt count

## Testing

Run the deterministic test suite with:

```bash
cd /Users/user/Desktop/text-to-sql-agent
pytest -q
```

The tests cover:
- SQL safety validation for SELECT statements
- rejection of destructive SQL (`DROP`, `DELETE`, `UPDATE`)
- real DB access against the seeded `customers` table

## Troubleshooting

### `qwen2.5-coder:7b` not found

If the app fails with:

```text
Ollama request failed: model 'qwen2.5-coder:7b' not found
```

Pull the model and restart Ollama:

```bash
ollama pull qwen2.5-coder:7b
ollama serve
```

### `address already in use` on port 11434

If `ollama serve` reports port `11434` is already bound, stop the existing process:

```bash
pkill -f "ollama serve"
ollama serve
```

Then run the Streamlit app in another terminal.

## Notes

- The app is intentionally minimal and does not call the LLM from tests.
- The database is read-only in normal operation for safety.
- If you change the Ollama model, update `src/config.py` accordingly.
