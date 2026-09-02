.PHONY: db-up db-down migrate api web backend-check frontend-check test

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

migrate:
	uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head

api:
	uv run --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000

web:
	npm run dev --prefix apps/web

backend-check:
	uv run --project apps/api ruff check apps/api/src tests/backend
	uv run --project apps/api ruff format --check apps/api/src tests/backend
	uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src
	APP_ENV=test AUTH_MODE=test AI_PROVIDER_MODE=fake uv run --env-file .env --project apps/api pytest

frontend-check:
	npm run lint --prefix apps/web
	npm run typecheck --prefix apps/web
	npm run build --prefix apps/web

test: backend-check frontend-check
