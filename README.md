# Text-to-SQL Agent

A local LLM-powered **Text-to-SQL agent** that converts natural-language questions into safe, executable SQL, runs the query against a SQLite e-commerce database, and explains the result in plain English.

The entire application runs locally using **Ollama** — no API keys, cloud services, or per-query costs.

Built as an evolution of [RominaElenaMendezEscobar/text-to-sql](https://github.com/RominaElenaMendezEscobar/text-to-sql), restructured into a small self-correcting agent with SQL safety guardrails, automated retries, database execution, and a custom Streamlit chat interface.

---

## Features

- **Natural-language to SQL** — ask questions such as *"Which product category has the highest total revenue?"* and receive a real `SELECT` query.
- **Self-correcting agent loop** — if generated SQL fails validation or database execution, the agent retries with the error fed back to the model, up to the configured retry limit.
- **SQL safety guardrails** — only read-only `SELECT` statements are executed. Destructive statements such as `DROP`, `DELETE`, and `UPDATE` are blocked before reaching the database.
- **Live schema context** — the agent reads the current SQLite schema and provides it to the model when generating SQL.
- **Result explanation** — successful query results are converted into a plain-English explanation.
- **Chat-style UI** — Streamlit UI with custom CSS, styled chat bubbles, and cards for SQL, results, and explanations.
- **100% local and free** — powered by Ollama and a locally running open-source model.
- **Automated tests** — pytest tests cover SQL safety checks and database execution against the seeded data.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Ollama — `qwen2.5-coder:7b` |
| Database | SQLite |
| UI | Streamlit + custom CSS |
| Language | Python 3.11 |
| Testing | pytest |

No Docker, backend server, or paid API is required.

---

## Project Structure

```text
text-to-sql-agent/
├── requirements.txt
├── .gitignore
│
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
│
├── data/
│   └── seed_db.py           # Generates the sample SQLite database
│
├── src/
│   ├── config.py            # Model name, DB path, retry limit
│   ├── db.py                # Read-only SQLite connection and query execution
│   ├── schema.py             # Reads live database schema
│   ├── prompts.py            # LLM prompt templates
│   ├── agent.py               # Generate → validate → execute → retry → explain
│   ├── ui_components.py       # Chat UI components and styling
│   └── app.py                # Streamlit application entry point
│
└── tests/
    └── test_agent.py        # SQL safety and database tests
```

---

## Database

The sample e-commerce database contains four related tables:

```text
customers
    │
    └── orders
          │
          └── order_items
                  │
                  └── products
```

The database is seeded with approximately:

- 15 customers
- 10 products
- 30 orders

The database file itself is generated locally by `data/seed_db.py` and is intentionally excluded from Git because it is reproducible.

---

## How the Agent Works

```text
                ┌──────────────────┐
                │ Natural Language │
                │     Question     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  Live DB Schema  │
                │     Context      │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   Local LLM      │
                │ Qwen2.5-Coder    │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  SQL Safety      │
                │    Validator     │
                └────────┬─────────┘
                         │
                  ┌──────┴──────┐
                  │             │
                Unsafe         Safe
                  │             │
                  ▼             ▼
                Reject       SQLite
                                │
                         ┌──────┴──────┐
                         │             │
                       Error        Success
                         │             │
                         ▼             ▼
                    Retry with     Explain
                    DB error       result
                         │
                         └──────►
```

### Agent loop

1. Receive the user's natural-language question.
2. Load the current database schema.
3. Ask the local LLM to generate SQL.
4. Validate the generated SQL.
5. Reject unsafe/destructive SQL before execution.
6. Execute valid SQL against SQLite.
7. If execution fails, feed the database error back to the model.
8. Retry up to the configured retry limit.
9. Explain the successful result in plain English.

The important design principle is that **LLM-generated SQL is never trusted blindly**. A deterministic safety layer sits between SQL generation and database execution.

---

## SQL Safety

The application is designed for read-only database querying.

Allowed:

```sql
SELECT *
FROM products;
```

Subqueries are also supported when they remain read-only:

```sql
SELECT name
FROM products
WHERE price > (
    SELECT AVG(price)
    FROM products
);
```

Destructive statements are rejected before reaching SQLite:

```sql
DROP TABLE products;
DELETE FROM customers;
UPDATE products SET price = 0;
```

This prevents the language model from directly modifying or destroying database data.

---

## Testing

The project uses **pytest** for deterministic tests of the SQL safety layer and database access.

Tests cover:

- Valid `SELECT` queries
- `SELECT` queries containing subqueries
- Blocking `DROP` statements
- Blocking `DELETE` statements
- Blocking `UPDATE` statements
- Query execution against the real seeded SQLite database

Run the test suite with:

```bash
pytest
```

---

## Setup

### 1. Install Ollama

Install Ollama for your operating system from:

https://ollama.com/

Then pull the recommended model:

```bash
ollama pull qwen2.5-coder:7b
```

> **System requirements:** The 7B model provides stronger SQL generation quality than smaller variants but requires more memory. A machine with at least 16GB of RAM is recommended for smooth local inference.

### 2. Clone the repository

```bash
git clone https://github.com/AshutoshPuri/Text-to-Sql-Agent.git
cd Text-to-Sql-Agent
```

### 3. Install Python dependencies

Python 3.11 is recommended.

```bash
pip install -r requirements.txt
```

### 4. Generate the sample database

```bash
python data/seed_db.py
```

This creates the local SQLite database used by the application.

### 5. Run the tests

```bash
pytest
```

### 6. Start Ollama

If Ollama is not already running:

```bash
ollama serve
```

Keep Ollama running in a separate terminal.

### 7. Launch the Streamlit application

```bash
streamlit run src/app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Example Queries

Try questions such as:

```text
Which product category has the highest total revenue?
```

```text
What are the top 5 products by total sales?
```

```text
Which customers have placed more than 3 orders?
```

```text
What is the average price of products in each category?
```

```text
Which products are more expensive than the average product price?
```

The application returns:

1. Generated SQL
2. Number of attempts
3. Query result
4. Plain-English explanation

If the question cannot be answered using the available database schema, the agent reports that instead of intentionally guessing.

---

## Demo

Add a screenshot of the application here:

```text
docs/demo.png
```

Then display it in the README with:

```markdown
![Text-to-SQL Agent Demo](docs/demo.png)
```

A useful screenshot should show the complete flow:

**Natural-language question → Generated SQL → Query result → Explanation**

---

## Configuration

The main configuration is available in:

```text
src/config.py
```

You can configure:

| Setting | Purpose |
|---|---|
| `MODEL_NAME` | Ollama model used for SQL generation |
| `MAX_RETRIES` | Maximum self-correction attempts |
| `DB_PATH` | Path to the SQLite database |

---

## Security & GitHub Safety

The repository intentionally does **not** commit generated database files or secrets.

The `.gitignore` excludes:

```text
.env
.env.*
*.key
*.pem
data/ecommerce.db
*.db
*.sqlite
*.sqlite3
.streamlit/secrets.toml
```

The sample database can always be regenerated using:

```bash
python data/seed_db.py
```

Before pushing changes, verify:

```bash
git status
```

and make sure no secrets, `.env` files, or database files are staged.

---

## Limitations

- Single SQLite database and schema.
- Not currently designed for multi-database or schema switching.
- Complex multi-join queries may still require one or more self-correction attempts.
- No authentication or multi-user support.
- Designed primarily as a local/portfolio project.

---

## Future Improvements

Potential future improvements include:

- PostgreSQL and MySQL support
- Multi-database selection
- Query-result visualizations
- Conversation memory
- Query caching
- More advanced SQL parsing/AST-based validation
- Human approval for sensitive queries
- Automated Text-to-SQL evaluation benchmarks
- GitHub Actions for automated testing

---

## Design Decisions

### Why Ollama?

Ollama allows the project to run an LLM locally without requiring an external API or per-request charges.

### Why SQLite?

SQLite keeps the project lightweight, portable, and easy to reproduce. The sample database can be generated entirely from the repository.

### Why a local model?

The project focuses on demonstrating the complete Text-to-SQL pipeline without depending on a paid cloud API.

### Why a safety layer?

LLM-generated code should not be treated as trusted executable input. The SQL validator provides a deterministic control point before generated SQL reaches the database.

---

## License

Personal/portfolio project. Feel free to fork and adapt.

---

## Author

**Ashutosh Puri**

B.Tech — Data Science & Engineering

GitHub: [AshutoshPuri](https://github.com/AshutoshPuri)
