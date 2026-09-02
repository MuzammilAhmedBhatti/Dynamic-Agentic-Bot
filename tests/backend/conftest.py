from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import httpx
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("AUTH_MODE", "test")
os.environ.setdefault("AI_PROVIDER_MODE", "fake")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://dynamic_agentic:phase1_test@127.0.0.1:54329/dynamic_agentic",
)
_source_database_url = make_url(os.environ["DATABASE_URL"])
_configured_test_url = os.environ.get("TEST_DATABASE_URL")
if _configured_test_url:
    _test_database_url = make_url(_configured_test_url)
    if not (_test_database_url.database or "").endswith("_test"):
        raise RuntimeError(
            "TEST_DATABASE_URL must use a database name ending in '_test'."
        )
else:
    source_database_name = _source_database_url.database or "dynamic_agentic"
    _test_database_url = _source_database_url.set(
        database=f"{source_database_name}_test"
    )
os.environ["DATABASE_URL"] = _test_database_url.render_as_string(hide_password=False)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
os.environ.setdefault("LOCAL_STORAGE_ROOT", "/tmp/dynamic-agentic-bot-test-objects")

from dynamic_agentic_api.db.session import async_session_factory
from dynamic_agentic_api.main import app
from dynamic_agentic_api.services import get_ai_services
from dynamic_agentic_api.vector_store.service import FakeVectorStore


async def _ensure_test_database_exists() -> None:
    database_name = _test_database_url.database or ""
    if not re.fullmatch(r"[a-zA-Z0-9_]+_test", database_name):
        raise RuntimeError("Refusing to prepare a test database with an unsafe name.")
    connection = await asyncpg.connect(
        user=_test_database_url.username,
        password=_test_database_url.password,
        host=_test_database_url.host,
        port=_test_database_url.port,
        database="postgres",
    )
    try:
        exists = await connection.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", database_name
        )
        if not exists:
            await connection.execute(f'CREATE DATABASE "{database_name}"')
    finally:
        await connection.close()


def _migrate_test_database() -> None:
    project_root = Path(__file__).resolve().parents[2]
    command.upgrade(Config(str(project_root / "apps/api/alembic.ini")), "head")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepared_test_database() -> AsyncIterator[None]:
    await _ensure_test_database_exists()
    await asyncio.to_thread(_migrate_test_database)
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_database(prepared_test_database: None) -> AsyncIterator[None]:
    del prepared_test_database

    async def truncate() -> None:
        async with async_session_factory() as session:
            await session.execute(
                text(
                    "TRUNCATE TABLE experiments, agent_trace_events, agent_runs, document_chunks, "
                    "document_pages, documents, data_sources, personas, knowledge_bases, role_permissions, "
                    "membership_roles, permissions, roles, organization_memberships, "
                    "users, organizations RESTART IDENTITY CASCADE"
                )
            )
            await session.commit()
        vectors = get_ai_services().vectors
        if isinstance(vectors, FakeVectorStore):
            vectors.clear()

    await truncate()
    yield
    await truncate()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as value:
        yield value
