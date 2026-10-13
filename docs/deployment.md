# Deployment

## Local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8000
```

## Docker

```bash
docker compose up --build
```

## Production notes

- Point `DATABASE_URL` at Postgres (`postgresql+asyncpg://...`) for multi-instance.
- Set `APP_ENV=production`, `LOG_LEVEL=INFO`, `LLM_MODE=openai|ollama`.
- Put the API behind TLS and restrict CORS origins.
- Keep dry-run on until tool adapters talk to real clusters.
