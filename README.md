# 🗄️ Text-to-SQL Agent

A local, zero-cost agentic app that turns plain-English questions into SQL — ask a question about an e-commerce database and get back the generated SQL, the live result, and a plain-English explanation. Runs entirely on your machine, no API keys, no cloud costs.

Built as an evolution of [RominaElenaMendezEscobar/text-to-sql](https://github.com/RominaElenaMendezEscobar/text-to-sql), restructured into a small self-correcting agent with a polished chat UI.

---

## Features

- **Natural-language to SQL** — ask questions like *"Which product category has the highest total revenue?"* and get back a real `SELECT` query.
- **Self-correcting agent loop** — if the generated SQL fails or is unsafe, the agent automatically retries (up to 2 times), feeding the database error back to the model to fix itself. No manual debugging needed.
- **SQL safety guardrails** — only read-only `SELECT` statements are ever executed; destructive statements (`DROP`, `DELETE`, `UPDATE`, etc.) are blocked before they reach the database.
- **Chat-style UI** — built in Streamlit with a custom theme, styled chat bubbles, and card-based layout for SQL, results, and explanations — not the default Streamlit look.
- **Runs 100% locally, 100% free** — powered by [Ollama](https://ollama.com) running a local open-source model. No OpenAI/Anthropic key, no per-query cost, no internet dependency once set up.

---

## Tech stack

| Layer | Choice |
|---|---|
| LLM | Ollama (local) — default `qwen2.5-coder:7b` |
| Database | SQLite |
| UI | Streamlit + custom CSS theme |
| Language | Python 3.11 |
| Tests | pytest |

No Docker, no backend server, no paid APIs — the whole stack is a handful of Python files plus Ollama.

---

## Project structure

```
text-to-sql-agent/
├── requirements.txt
├── .streamlit/
│   └── config.toml          # app theme (colors, font)
├── data/
│   └── seed_db.py           # generates data/ecommerce.db with sample data
├── src/
│   ├── config.py             # model name, DB path, retry limit
│   ├── db.py                 # read-only SQLite connection + query execution
│   ├── schema.py              # reads live DB schema for prompt context
│   ├── prompts.py             # all LLM prompt templates
│   ├── agent.py                # generate → validate → execute → retry → explain
│   ├── ui_components.py        # styled chat bubbles, cards, sidebar, CSS
│   └── app.py                   # Streamlit entry point
└── tests/
    └── test_agent.py            # deterministic tests (safety checks, DB access)
```

---

## Database schema

The sample e-commerce database has 4 tables: `customers`, `products`, `orders`, and `order_items`, linked by foreign keys. Seeded with ~15 customers, 10 products, and 30 orders so there's enough data to ask meaningful questions.

---

## Setup

> **Note for 8GB MacBook Air (M1/M2) or similar low-RAM machines:** use the default `qwen2.5-coder:3b` model, not a 7B+ model — larger models can exhaust available memory and freeze the system. Close other heavy apps (browser, Docker, IDEs) before running.

1. **Install Ollama** and pull the model:
   ```bash
   # https://ollama.com — install for your OS
   ollama pull qwen2.5-coder:3b
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed the sample database:**
   ```bash
   python data/seed_db.py
   ```

4. **Run the tests** (optional but recommended):
   ```bash
   pytest
   ```

5. **Start Ollama** (in a separate terminal, if not already running):
   ```bash
   ollama serve
   ```

6. **Launch the app:**
   ```bash
   streamlit run src/app.py
   ```

The app opens at `http://localhost:8501`.

---

## Usage

- Type a question in the chat box at the bottom, or click one of the example questions in the sidebar.
- Each answer shows: the generated SQL, how many attempts it took (with a note if it self-corrected), the result table, and a plain-English explanation.
- If a question can't be answered from the schema, the agent will say so directly instead of guessing.

---

## How the agent works

```
Question
   │
   ▼
Generate SQL (LLM + live schema context)
   │
   ▼
Safety check (block destructive statements) ──fail──┐
   │ pass                                            │
   ▼                                                  │
Execute against SQLite (read-only) ──fail─────────────┤
   │ success                                          │
   │                                     retry (max 2, with error fed back)
   ▼                                                  │
Explain result in plain English  ◀────────────────────┘
```

---

## Configuration

Edit `src/config.py` to change:
- `MODEL_NAME` — which Ollama model to use
- `MAX_RETRIES` — how many self-correction attempts before giving up
- `DB_PATH` — which SQLite file to query

---

## Limitations

- Single-database, single-schema setup — not built for multi-database or schema-switching yet.
- Local model quality (especially at smaller sizes like 3B) is lower than hosted large models — complex multi-join questions may need a retry or two.
- No authentication or multi-user support — designed as a personal/local tool.

---

## License

Personal/portfolio project. Feel free to fork and adapt.
