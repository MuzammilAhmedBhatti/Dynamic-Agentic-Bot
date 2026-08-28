# Dynamic Agentic Bot

Secure, multi-tenant Dynamic Agentic AI Intelligence Platform.

## Milestone status

Milestone 4 adds an isolated tenant-scoped AI Lab, persisted Evaluation Center, and security/resource hardening while preserving the Milestone 3 production assistant. Labs cover safe data preparation, classical ML, a bounded PyTorch MLP, NLP, and optional cached Transformer inference. Evaluations cover RAG/citations, configurations, LLM/prompt versions, persona/router, database, math, and adversarial safety. Deployment infrastructure remains Milestone 5 and is not authorized.

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
10. To test the Database Agent, expand **Register PostgreSQL source** in Chat and submit the configured `DATABASE_URL`, schema `demo_business`, and tables `customers,orders,sales`. The credential is encrypted and is never returned to the browser.
11. Try `What is the percentage increase from 240 to 300?`, `How many orders are in the demo database?`, and a question grounded in the uploaded PDF. AUTO selects the persona and route; selectors allow an approved manual override.
12. Open `/ai-lab` to run bounded reproducible experiments and `/evaluation` to run benchmarks and inspect tenant-owned history.

`APP_ENV=test` is only for the explicit local test-session adapter; managed Vertex/Pinecone providers remain real when `AI_PROVIDER_MODE=managed`. Staging/production require `APP_ENV=staging|production`, `AUTH_MODE=oidc`, HTTPS origins, and managed AI mode.

Authenticate ADC with `gcloud auth application-default login` for local development. Enable Vertex AI in the selected project. Create one Pinecone index using the configured embedding dimension and similarity metric, then set `PINECONE_API_KEY`, `PINECONE_INDEX`, and optionally `PINECONE_INDEX_HOST`. Credentials remain server-side.

Development API documentation is available at `http://localhost:8000/docs`. Health endpoints are `GET /health` and `GET /api/v1/health`; readiness is `GET /api/v1/ready`.

## Quality checks

```text
uv run --project apps/api ruff check apps/api/src tests/backend
uv run --project apps/api ruff format --check apps/api/src tests/backend
uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src
uv run --project apps/api pytest tests/backend
npm run lint --prefix apps/web
npm run typecheck --prefix apps/web
npm run build --prefix apps/web
```

Run the credential-gated managed-provider test with `RUN_MANAGED_AI_INTEGRATION=1 uv run --project apps/api pytest -m managed_integration tests/backend/test_managed_ai_integration.py`.

OpenAI and Anthropic models appear as unavailable capability targets until their real adapters and server-side credentials are configured. Gemini through Vertex AI remains the production provider; no fake provider response is used outside tests.

Do not begin Milestone 5 without explicit approval.
