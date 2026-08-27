# Dynamic Agentic Bot

Secure, multi-tenant foundation for the Dynamic Agentic AI Intelligence Platform.

## Phase status

Phase 1 establishes the FastAPI backend, PostgreSQL tenant/RBAC schema, provider-neutral authentication boundary, authorization enforcement, Next.js application shell, local database, tests, and CI. It intentionally contains no RAG, Pinecone, LangGraph, LLM, OCR, queue, Redis, or AI Lab implementation.

## Prerequisites

- Python 3.12
- `uv`
- Node.js 22 or newer
- Docker with Compose

## Local setup

1. Copy `.env.example` to `.env` and replace `CHANGE_ME` with a local password.
2. Start PostgreSQL: `docker compose up -d postgres`.
3. Install backend dependencies: `uv sync --project apps/api --all-groups`.
4. Apply migrations: `uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head`.
5. Start the API: `uv run --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000`.
6. Install frontend dependencies: `npm ci --prefix apps/web`.
7. Start the web application: `npm run dev --prefix apps/web`.

Development API documentation is available at `http://localhost:8000/docs`. Health endpoints are `GET /health` and `GET /api/v1/health`; readiness is `GET /api/v1/ready`.

## Quality checks

```text
uv run --project apps/api ruff check apps/api/src tests/backend
uv run --project apps/api ruff format --check apps/api/src tests/backend
uv run --project apps/api mypy apps/api/src
uv run --project apps/api pytest
npm run lint --prefix apps/web
npm run typecheck --prefix apps/web
npm run build --prefix apps/web
```

Do not begin Phase 2 without explicit approval.
