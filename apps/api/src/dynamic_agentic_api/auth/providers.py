from __future__ import annotations

import uuid
from typing import Protocol

from fastapi import Request

from dynamic_agentic_api.auth.domain import AuthenticatedUser
from dynamic_agentic_api.config import Settings
from dynamic_agentic_api.errors import AppError


class IdentityProvider(Protocol):
    async def authenticate(self, request: Request) -> AuthenticatedUser: ...


class DisabledIdentityProvider:
    async def authenticate(self, request: Request) -> AuthenticatedUser:
        raise AppError(
            status_code=401,
            code="AUTHENTICATION_REQUIRED",
            message="Authentication is required.",
        )


class TestHeaderIdentityProvider:
    """Explicit test-only identity source; Settings forbids it outside APP_ENV=test."""

    async def authenticate(self, request: Request) -> AuthenticatedUser:
        raw_user_id = request.headers.get("X-Test-User-ID")
        if not raw_user_id:
            raise AppError(
                status_code=401,
                code="AUTHENTICATION_REQUIRED",
                message="Authentication is required.",
            )
        try:
            user_id = uuid.UUID(raw_user_id)
        except ValueError as exc:
            raise AppError(
                status_code=401,
                code="INVALID_TEST_IDENTITY",
                message="The test identity is invalid.",
            ) from exc
        return AuthenticatedUser(
            user_id=user_id,
            external_subject=str(user_id),
            identity_provider="explicit-test-provider",
        )


class OidcIdentityProviderBoundary:
    """Fail-closed Phase 1 seam for Google Identity Platform or another OIDC provider."""

    async def authenticate(self, request: Request) -> AuthenticatedUser:
        raise AppError(
            status_code=503,
            code="OIDC_NOT_CONNECTED",
            message="The configured identity provider is not connected.",
            retryable=False,
        )


def build_identity_provider(settings: Settings) -> IdentityProvider:
    if settings.auth_mode == "test":
        return TestHeaderIdentityProvider()
    if settings.auth_mode == "oidc":
        return OidcIdentityProviderBoundary()
    return DisabledIdentityProvider()
