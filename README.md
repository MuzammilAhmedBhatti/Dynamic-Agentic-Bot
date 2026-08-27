# Dynamic Agentic Bot

Secure, multi-tenant Dynamic Agentic AI Intelligence Platform.

## Milestone status

Milestone 2 implements the first working PDF -> extraction/rendering -> Vertex embeddings -> Pinecone -> retrieval -> Gemini -> grounded answer -> exact-page citation/preview flow, orchestrated by LangGraph with a safe WebSocket trace. The next milestone is not authorized.

## Prerequisites

- Python 3.12
- `uv`
- Node.js 22 or newer
- Docker with Compose
- A GCP project with Vertex AI access and local Application Default Credentials
- A Pinecone serverless dense index whose dimension matches `VERTEX_EMBEDDING_DIMENSION`

## Local setup

1. Copy `.env.example` to `.env`, replace `CHANGE_ME`, set `APP_ENV=test` and `AUTH_MODE=test` for the local session UI, and fill the managed AI variables.
2. Start PostgreSQL: `docker compose up -d postgres`.
3. Install backend dependencies: `uv sync --project apps/api --all-groups`.
4. Apply migrations: `uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head`.
5. Create a local tenant/user: `uv run --project apps/api python -m dynamic_agentic_api.dev_bootstrap` and retain the two printed IDs.
6. Start the API: `uv run --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000`.
7. Install frontend dependencies: `npm ci --prefix apps/web`.
8. Start the web application: `npm run dev --prefix apps/web`.
9. Open `http://localhost:3000/knowledge-base`, connect with the printed IDs, create a KB, and upload a PDF. Then use `/chat` with the same IDs.

`APP_ENV=test` is only for the explicit local test-session adapter; managed Vertex/Pinecone providers remain real when `AI_PROVIDER_MODE=managed`. Staging/production require `APP_ENV=staging|production`, `AUTH_MODE=oidc`, HTTPS origins, and managed AI mode.

Authenticate ADC with `gcloud auth application-default login` for local development. Enable Vertex AI in the selected project. Create one Pinecone index using the configured embedding dimension and similarity metric, then set `PINECONE_API_KEY`, `PINECONE_INDEX`, and optionally `PINECONE_INDEX_HOST`. Credentials remain server-side.

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

Run the credential-gated managed-provider test with `RUN_MANAGED_AI_INTEGRATION=1 uv run --project apps/api pytest -m managed_integration tests/backend/test_managed_ai_integration.py`.

Do not begin Milestone 3 without explicit approval.
