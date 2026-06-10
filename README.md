# Strands Agent API

A FastAPI service that exposes a conversational agent powered by [Strands Agents](https://strandsagents.com) and OpenAI `gpt-4o-mini`. Conversation history is persisted per session in PostgreSQL.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker & Docker Compose
- An OpenAI API key

## Running with Docker (recommended)

```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env

docker compose up --build
```

Apply the database schema on first run:

```bash
docker compose exec -T db psql -U strands strandsagent < app/session/schema.sql
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI) at `http://localhost:8000/docs`.

The `app/` directory is mounted into the container, so code changes reload automatically without rebuilding.

## Running locally

```bash
uv sync
cp .env.example .env
# Set OPENAI_API_KEY and DATABASE_URL in .env

uv run uvicorn app.main:app --reload
```

## Usage

Send a question to start or continue a session:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather in Madrid?", "session_id": "my-session"}'
```

Omit `session_id` to start a new session — the response will include the generated ID to use in follow-up requests.

```json
{
  "answer": "The weather in Madrid is Sunny, 22°C.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Available tools

| Tool | Description |
|---|---|
| `get_weather` | Live weather for any city via wttr.in |
| `get_current_time` | Current date and time |
| `convert_temperature` | Celsius to Fahrenheit |
| `get_stock_price` | Simulated stock price for AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA |
| `roll_dice` | Roll N dice with configurable sides |
| `flip_coin` | Flip one or more coins |
| `get_fun_fact` | Fun fact by topic: `space`, `animals`, `food`, `math`, `history` |
| `calculate_tip` | Tip calculator with optional bill splitting |

## Development

```bash
# Lint and auto-fix
uv run ruff check --fix app/

# Format
uv run ruff format app/
```

Ruff is configured in `pyproject.toml` with line length 88, double quotes, and import sorting.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/ask` | Send a question to the agent |
