# Ops Tool-Calling Agent

Production-shaped SRE co-pilot: LLM plans multi-step tool calls, humans approve, executions support dry-run, and every action is audited.

![CI](https://img.shields.io/badge/CI-pytest%20%7C%20ruff%20%7C%20mypy-22c55e)
![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6)
![License](https://img.shields.io/badge/license-MIT-informational)

## Why this exists

Most "AI ops" demos jump straight from a prompt to a shell command. This project models how real teams actually work:
**plan → human approval → dry-run → execute → audit**.

## Features

- Tool registry with risk labels (`low` / `medium` / `high`)
- LLM planner (mock / OpenAI / Ollama) returning structured JSON plans
- Approval gate + dry-run execution
- Durable SQLite storage (Postgres-ready URL)
- Request IDs, latency headers, structured logs
- Operator UI + OpenAPI (`/docs`)
- CI workflow, coverage-friendly tests, Docker healthchecks

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8000
```

Open http://127.0.0.1:8000 — or API docs at `/docs`.

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest -q --cov=backend
```

## Project layout

```text
backend/
  api/           # HTTP routers
  llm/           # provider implementations
  services/      # orchestration
  tools/         # executable tool registry
  templates/     # operator UI
docs/            # architecture, API, deployment
tests/           # unit + flow + perf smoke
```

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Deployment](docs/deployment.md)

## License

MIT — see [LICENSE](LICENSE).
