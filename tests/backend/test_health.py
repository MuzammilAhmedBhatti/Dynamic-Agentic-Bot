from __future__ import annotations

import httpx


async def test_root_and_versioned_health(client: httpx.AsyncClient) -> None:
    for path in ("/health", "/api/v1/health"):
        response = await client.get(path)
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "Dynamic Agentic Bot API",
            "environment": "test",
        }
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["x-request-id"]


async def test_readiness_checks_postgresql(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ready"}


async def test_invalid_request_id_is_replaced(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/health", headers={"X-Request-ID": "unsafe request id"}
    )
    assert response.status_code == 200
    assert response.headers["x-request-id"] != "unsafe request id"


async def test_unknown_route_uses_safe_error_envelope(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/missing")
    assert response.status_code == 404
    body = response.json()["error"]
    assert body["code"] == "NOT_FOUND"
    assert body["message"] == "The requested resource was not found."
    assert "trace_id" in body
    assert "Traceback" not in response.text
