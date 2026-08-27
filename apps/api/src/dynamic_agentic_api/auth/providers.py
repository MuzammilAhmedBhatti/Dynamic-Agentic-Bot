from __future__ import annotations

import asyncio
import uuid
from typing import Protocol

import httpx
import jwt
from jwt import PyJWKClient
from starlette.requests import HTTPConnection

from dynamic_agentic_api.auth.domain import AuthenticatedUser
from dynamic_agentic_api.config import Settings
from dynamic_agentic_api.errors import AppError


class IdentityProvider(Protocol):
    async def authenticate(self, request: HTTPConnection) -> AuthenticatedUser: ...


class DisabledIdentityProvider:
    async def authenticate(self, request: HTTPConnection) -> AuthenticatedUser:
        raise AppError(
            status_code=401,
            code="AUTHENTICATION_REQUIRED",
            message="Authentication is required.",
        )


class TestHeaderIdentityProvider:
    """Explicit test-only identity source; Settings forbids it outside APP_ENV=test."""

    async def authenticate(self, request: HTTPConnection) -> AuthenticatedUser:
        raw_user_id = request.headers.get("X-Test-User-ID") or request.cookies.get(
            "dynamic_agentic_test_user"
        )
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
    """Validate standards-based OIDC bearer JWTs without provider domain coupling."""

    def __init__(self, settings: Settings) -> None:
        if not settings.oidc_issuer_url or not settings.oidc_client_id:
            raise ValueError("OIDC settings are incomplete")
        self._issuer = settings.oidc_issuer_url.rstrip("/")
        self._audience = settings.oidc_client_id
        self._jwks_url = settings.oidc_jwks_url
        self._timeout = settings.external_call_timeout_seconds
        self._jwk_client: PyJWKClient | None = None

    async def authenticate(self, request: HTTPConnection) -> AuthenticatedUser:
        authorization = request.headers.get("Authorization", "")
        token = request.cookies.get("dynamic_agentic_access_token")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise AppError(
                status_code=401,
                code="AUTHENTICATION_REQUIRED",
                message="Authentication is required.",
            )
        try:
            jwk_client = await self._get_jwk_client()
            signing_key = await asyncio.to_thread(jwk_client.get_signing_key_from_jwt, token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "iss", "sub", "aud"]},
            )
        except (jwt.PyJWTError, httpx.HTTPError, KeyError, ValueError) as exc:
            raise AppError(
                status_code=401,
                code="INVALID_IDENTITY_TOKEN",
                message="The identity token is invalid or expired.",
            ) from exc
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise AppError(
                status_code=401,
                code="INVALID_IDENTITY_TOKEN",
                message="The identity token is invalid or expired.",
            )
        return AuthenticatedUser(
            user_id=None,
            external_subject=subject,
            identity_provider=self._issuer,
        )

    async def _get_jwk_client(self) -> PyJWKClient:
        if self._jwk_client is not None:
            return self._jwk_client
        jwks_url = self._jwks_url
        if not jwks_url:
            discovery_url = f"{self._issuer}/.well-known/openid-configuration"
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(discovery_url)
                response.raise_for_status()
                discovered = response.json().get("jwks_uri")
            if not isinstance(discovered, str) or not discovered.startswith("https://"):
                raise ValueError("OIDC discovery did not return a secure JWKS URL")
            jwks_url = discovered
        self._jwk_client = PyJWKClient(jwks_url, timeout=self._timeout)
        return self._jwk_client


def build_identity_provider(settings: Settings) -> IdentityProvider:
    if settings.auth_mode == "test":
        return TestHeaderIdentityProvider()
    if settings.auth_mode == "oidc":
        return OidcIdentityProviderBoundary(settings)
    return DisabledIdentityProvider()
