from __future__ import annotations

import uuid

import httpx
import pymupdf
import pytest
from dynamic_agentic_api.db.models import (
    AgentTraceEvent,
    Document,
    DocumentChunk,
    MembershipRole,
    Organization,
    OrganizationMembership,
    Permission,
    Role,
    RolePermission,
    User,
)
from dynamic_agentic_api.db.session import async_session_factory
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.main import app
from dynamic_agentic_api.services import get_ai_services
from dynamic_agentic_api.tracing.service import SafeTraceEvent
from sqlalchemy import select
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


async def seed_tenant(label: str = "Tenant") -> tuple[uuid.UUID, uuid.UUID]:
    async with async_session_factory() as session:
        organization = Organization(
            name=label, slug=f"{label.casefold()}-{uuid.uuid4().hex[:8]}"
        )
        user = User(
            identity_provider="explicit-test-provider",
            external_subject=uuid.uuid4().hex,
            email_normalized=f"{uuid.uuid4().hex[:8]}@example.com",
        )
        session.add_all([organization, user])
        await session.flush()
        membership = OrganizationMembership(
            organization_id=organization.id, user_id=user.id
        )
        role = Role(organization_id=organization.id, name="knowledge-user")
        session.add_all([membership, role])
        await session.flush()
        session.add(
            MembershipRole(
                membership_id=membership.id,
                role_id=role.id,
                organization_id=organization.id,
            )
        )
        for code in ["knowledge_base.read", "knowledge_base.write", "chat.execute"]:
            permission = await session.scalar(
                select(Permission).where(Permission.code == code)
            )
            if permission is None:
                permission = Permission(code=code, description=code)
                session.add(permission)
                await session.flush()
            session.add(RolePermission(role_id=role.id, permission_id=permission.id))
        await session.commit()
        return organization.id, user.id


def make_pdf(text: str, *, pages: int = 1) -> bytes:
    document = pymupdf.open()
    try:
        for page_number in range(pages):
            page = document.new_page()
            page.insert_text((72, 72), f"{text} Page marker {page_number + 1}.")
        return document.tobytes()
    finally:
        document.close()


async def create_kb(
    client: httpx.AsyncClient,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    name: str = "Legal",
) -> str:
    response = await client.post(
        f"/api/v1/organizations/{organization_id}/knowledge-bases",
        headers={"X-Test-User-ID": str(user_id)},
        json={"name": name},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


async def upload_pdf(
    client: httpx.AsyncClient,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    knowledge_base_id: str,
    text: str,
    filename: str = "policy.pdf",
) -> dict[str, object]:
    response = await client.post(
        f"/api/v1/organizations/{organization_id}/knowledge-bases/{knowledge_base_id}/documents",
        headers={"X-Test-User-ID": str(user_id)},
        files={"file": (filename, make_pdf(text), "application/pdf")},
    )
    assert response.status_code == 202, response.text
    return response.json()


async def test_upload_ingestion_chat_citation_preview_and_trace(
    client: httpx.AsyncClient,
) -> None:
    organization_id, user_id = await seed_tenant()
    kb_id = await create_kb(client, organization_id, user_id)
    document = await upload_pdf(
        client,
        organization_id,
        user_id,
        kb_id,
        "The contractual retention period is seven years after termination.",
        "../unsafe policy.pdf",
    )
    assert document["filename"] == "unsafe policy.pdf"
    listing = await client.get(
        f"/api/v1/organizations/{organization_id}/knowledge-bases/{kb_id}/documents",
        headers={"X-Test-User-ID": str(user_id)},
    )
    assert listing.status_code == 200
    ready = listing.json()[0]
    assert ready["status"] == "ready"
    assert ready["page_count"] == 1
    assert ready["embedding_model"] == "fake-embedding-v1"
    reindexed = await client.post(
        f"/api/v1/organizations/{organization_id}/documents/{ready['id']}/reindex",
        headers={"X-Test-User-ID": str(user_id)},
    )
    assert reindexed.status_code == 202
    assert reindexed.json()["status"] == "queued"
    refreshed = await client.get(
        f"/api/v1/organizations/{organization_id}/knowledge-bases/{kb_id}/documents",
        headers={"X-Test-User-ID": str(user_id)},
    )
    assert refreshed.json()[0]["status"] == "ready"

    created = await client.post(
        f"/api/v1/organizations/{organization_id}/chat/runs",
        headers={"X-Test-User-ID": str(user_id)},
        json={"knowledge_base_id": kb_id},
    )
    run_id = created.json()["run_id"]
    answer = await client.post(
        f"/api/v1/organizations/{organization_id}/chat/runs/{run_id}/execute",
        headers={"X-Test-User-ID": str(user_id)},
        json={"question": "What is the contractual retention period?"},
    )
    assert answer.status_code == 200, answer.text
    body = answer.json()
    assert body["support"] == "grounded"
    assert body["sources"][0]["document_name"] == "unsafe policy.pdf"
    assert body["sources"][0]["page_number"] == 1
    preview = await client.get(
        body["sources"][0]["preview_reference"],
        headers={"X-Test-User-ID": str(user_id)},
    )
    assert preview.status_code == 200
    assert preview.headers["content-type"] == "image/png"
    assert preview.content.startswith(b"\x89PNG")

    async with async_session_factory() as session:
        chunk = await session.scalar(select(DocumentChunk))
        assert chunk is not None
        assert chunk.page_number == 1
        assert chunk.chunker_version == "recursive-page-v1"
        event_types = list(
            await session.scalars(
                select(AgentTraceEvent.event_type)
                .where(AgentTraceEvent.run_id == uuid.UUID(run_id))
                .order_by(AgentTraceEvent.sequence)
            )
        )
    assert event_types == [
        "request_received",
        "authorization_passed",
        "persona_selection_started",
        "persona_selected",
        "router_completed",
        "retrieval_started",
        "retrieval_completed",
        "llm_started",
        "llm_completed",
        "citation_validation_completed",
        "suggestion_generation_completed",
        "response_completed",
    ]


async def test_upload_validation_and_duplicate_idempotency(
    client: httpx.AsyncClient,
) -> None:
    organization_id, user_id = await seed_tenant()
    kb_id = await create_kb(client, organization_id, user_id)
    headers = {"X-Test-User-ID": str(user_id)}
    invalid_mime = await client.post(
        f"/api/v1/organizations/{organization_id}/knowledge-bases/{kb_id}/documents",
        headers=headers,
        files={"file": ("not.pdf", b"text", "text/plain")},
    )
    assert invalid_mime.status_code == 415
    invalid_signature = await client.post(
        f"/api/v1/organizations/{organization_id}/knowledge-bases/{kb_id}/documents",
        headers=headers,
        files={"file": ("bad.pdf", b"not a pdf", "application/pdf")},
    )
    assert invalid_signature.status_code == 422
    pdf_data = make_pdf("A unique policy statement.")
    endpoint = (
        f"/api/v1/organizations/{organization_id}/knowledge-bases/{kb_id}/documents"
    )
    first_response = await client.post(
        endpoint,
        headers=headers,
        files={"file": ("policy.pdf", pdf_data, "application/pdf")},
    )
    second_response = await client.post(
        endpoint,
        headers=headers,
        files={"file": ("policy.pdf", pdf_data, "application/pdf")},
    )
    assert first_response.status_code == second_response.status_code == 202
    first, second = first_response.json(), second_response.json()
    assert first["id"] == second["id"]
    async with async_session_factory() as session:
        assert len(list(await session.scalars(select(Document)))) == 1


async def test_cross_tenant_resources_and_retrieval_are_denied(
    client: httpx.AsyncClient,
) -> None:
    first_org, first_user = await seed_tenant("First")
    first_kb = await create_kb(client, first_org, first_user, "First KB")
    await upload_pdf(
        client, first_org, first_user, first_kb, "The private launch code is ORCHID."
    )
    second_org, second_user = await seed_tenant("Second")
    second_kb = await create_kb(client, second_org, second_user, "Second KB")
    await upload_pdf(
        client, second_org, second_user, second_kb, "The public office opens on Monday."
    )

    denied = await client.get(
        f"/api/v1/organizations/{first_org}/knowledge-bases/{first_kb}/documents",
        headers={"X-Test-User-ID": str(second_user)},
    )
    assert denied.status_code == 403
    run = await client.post(
        f"/api/v1/organizations/{second_org}/chat/runs",
        headers={"X-Test-User-ID": str(second_user)},
        json={"knowledge_base_id": second_kb},
    )
    answer = await client.post(
        f"/api/v1/organizations/{second_org}/chat/runs/{run.json()['run_id']}/execute",
        headers={"X-Test-User-ID": str(second_user)},
        json={"question": "What is the private launch code?"},
    )
    assert answer.status_code == 200
    assert answer.json()["support"] == "unanswerable"
    assert "ORCHID" not in answer.text


async def test_auto_scope_searches_all_authorized_knowledge_bases(
    client: httpx.AsyncClient,
) -> None:
    organization_id, user_id = await seed_tenant("Auto Scope")
    first_kb = await create_kb(client, organization_id, user_id, "General Policies")
    second_kb = await create_kb(client, organization_id, user_id, "Technical Manuals")
    await upload_pdf(
        client,
        organization_id,
        user_id,
        first_kb,
        "Ordinary office supplies are stored in cabinet four.",
        "office.pdf",
    )
    await upload_pdf(
        client,
        organization_id,
        user_id,
        second_kb,
        "The Atlas beacon color is cobalt blue during normal operation.",
        "atlas-manual.pdf",
    )
    created = await client.post(
        f"/api/v1/organizations/{organization_id}/chat/runs",
        headers={"X-Test-User-ID": str(user_id)},
        json={"knowledge_base_id": None, "search_all_knowledge_bases": True},
    )
    assert created.status_code == 201, created.text
    answer = await client.post(
        f"/api/v1/organizations/{organization_id}/chat/runs/"
        f"{created.json()['run_id']}/execute",
        headers={"X-Test-User-ID": str(user_id)},
        json={"question": "What color is the Atlas beacon?"},
    )
    assert answer.status_code == 200, answer.text
    body = answer.json()
    assert body["support"] == "grounded"
    assert body["sources"][0]["document_name"] == "atlas-manual.pdf"
    assert "cobalt blue" in body["answer"]


async def test_document_answer_uses_safe_evidence_fallback_when_llm_is_unavailable(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    organization_id, user_id = await seed_tenant("Fallback")
    kb_id = await create_kb(client, organization_id, user_id, "Continuity")
    await upload_pdf(
        client,
        organization_id,
        user_id,
        kb_id,
        "The continuity recovery target is four hours.",
        "continuity.pdf",
    )
    provider = get_ai_services().llms.resolve(None, None)

    async def unavailable(*_: object, **__: object) -> None:
        raise AppError(
            status_code=503,
            code="LLM_PROVIDER_UNAVAILABLE",
            message="The language model is temporarily unavailable.",
            retryable=True,
        )

    monkeypatch.setattr(provider, "generate_grounded_answer", unavailable)
    created = await client.post(
        f"/api/v1/organizations/{organization_id}/chat/runs",
        headers={"X-Test-User-ID": str(user_id)},
        json={"knowledge_base_id": kb_id},
    )
    answer = await client.post(
        f"/api/v1/organizations/{organization_id}/chat/runs/"
        f"{created.json()['run_id']}/execute",
        headers={"X-Test-User-ID": str(user_id)},
        json={"question": "What is the continuity recovery target?"},
    )
    assert answer.status_code == 200, answer.text
    body = answer.json()
    assert body["support"] == "grounded"
    assert body["sources"][0]["document_name"] == "continuity.pdf"
    assert "temporarily unavailable" in body["answer"]
    assert "four hours" in body["answer"]


def test_websocket_trace_rejects_unauthenticated_connection() -> None:
    path = f"/api/v1/organizations/{uuid.uuid4()}/chat/runs/{uuid.uuid4()}/trace"
    with (
        TestClient(app) as client,
        pytest.raises(WebSocketDisconnect) as caught,
        client.websocket_connect(path, headers={"origin": "http://localhost:3000"}),
    ):
        pass
    assert caught.value.code == 4401


def test_live_trace_event_is_json_serializable() -> None:
    event = SafeTraceEvent(
        sequence=1,
        run_id=uuid.uuid4(),
        event_type="request_received",
        stage="security_input_guard",
        occurred_at="2026-08-27T00:00:00+00:00",
        duration_ms=1,
        safe_summary={},
    )
    assert isinstance(event.to_dict()["run_id"], str)
