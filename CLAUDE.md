# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run locally (requires .env with OPENAI_API_KEY and DATABASE_URL)
uv run uvicorn app.main:app --reload

# Run with Docker (app + postgres)
docker compose up --build

# Apply DB schema (first time, or after schema changes)
docker compose exec -T db psql -U strands strandsagent < app/session/schema.sql

# Lint / format
uv run ruff check --fix app/
uv run ruff format app/
```

There are no automated tests in this repository yet.

## Architecture

The service is a single POST endpoint (`/ask`) that wraps a [Strands](https://strandsagents.com) agent with conversation persistence.

**Request flow:**
1. `POST /ask` receives `{question, session_id?}` — generates a UUID session_id if omitted
2. `build_agent(session_id)` in `app/agent.py` constructs a fresh `Agent` instance per request, attaching a `PostgresSessionManager` keyed to that session
3. Strands' `RepositorySessionManager` (the base class) automatically loads prior messages from Postgres on `Agent.__init__` and appends new ones after each turn — no manual history management needed
4. The agent calls tools as needed, then returns a final text response

**Session persistence (`app/session/`):**
- `PostgresSessionManager` extends `RepositorySessionManager + SessionRepository` from the Strands SDK — the same pattern used by the built-in `FileSessionManager`
- Implements 8 CRUD methods against 3 tables: `sessions`, `session_agents`, `session_messages`
- All payloads are stored as JSONB using the domain objects' `to_dict()` / `from_dict()` methods
- Uses a single `psycopg` (sync) connection per request with `autocommit=True`
- Schema is in `app/session/schema.sql` — must be applied manually on first deploy

**Adding a tool:** define a function decorated with `@tool` in `app/agent.py` and add it to the `tools=[...]` list in `build_agent`. Strands generates the tool schema from the type hints and docstring automatically.

## Environment variables

| Variable | Required | Notes |
|---|---|---|
| `OPENAI_API_KEY` | yes | Passed to `OpenAIModel` |
| `DATABASE_URL` | yes | psycopg connection string; in docker-compose this is set to the `db` service |
