from __future__ import annotations

import os
from collections.abc import AsyncIterator

import httpx
import pytest_asyncio
from sqlalchemy import text

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("AUTH_MODE", "test")
os.environ.setdefault("AI_PROVIDER_MODE", "fake")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://dynamic_agentic:phase1_test@127.0.0.1:54329/dynamic_agentic",
)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
os.environ.setdefault("LOCAL_STORAGE_ROOT", "/tmp/dynamic-agentic-bot-test-objects")

from dynamic_agentic_api.db.session import async_session_factory
from dynamic_agentic_api.main import app
from dynamic_agentic_api.services import get_ai_services
from dynamic_agentic_api.vector_store.service import FakeVectorStore


@pytest_asyncio.fixture(autouse=True)
async def clean_database() -> AsyncIterator[None]:
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
