from __future__ import annotations

import pytest
from dynamic_agentic_api.config import Settings
from pydantic import ValidationError

BASE = {
    "database_url": "postgresql+asyncpg://user:password@localhost/database",
    "cors_origins": "https://app.example.com",
    "allowed_hosts": "app.example.com",
    "ai_provider_mode": "managed",
}


def test_production_requires_oidc() -> None:
    with pytest.raises(ValidationError, match="AUTH_MODE=oidc"):
        Settings(**BASE, app_env="production", auth_mode="disabled", _env_file=None)


def test_oidc_requires_issuer_and_client() -> None:
    with pytest.raises(ValidationError, match="OIDC_ISSUER_URL"):
        Settings(**BASE, app_env="production", auth_mode="oidc", _env_file=None)


def test_test_auth_is_rejected_outside_test() -> None:
    with pytest.raises(ValidationError, match="APP_ENV=test"):
        Settings(**BASE, app_env="development", auth_mode="test", _env_file=None)


def test_non_postgresql_database_is_rejected() -> None:
    with pytest.raises(ValidationError, match="PostgreSQL"):
        Settings(database_url="sqlite:///unsafe.db", _env_file=None)


def test_secure_production_configuration_is_valid() -> None:
    settings = Settings(
        **BASE,
        app_env="production",
        auth_mode="oidc",
        oidc_issuer_url="https://identity.example.com",
        oidc_client_id="dynamic-agentic-web",
        data_source_encryption_key="bkx2TEZBWkZ1RXhBZ2k5eWQ3MklVVUVGcVhHS25zVXlTTWpNODAxST0=",
        _env_file=None,
    )
    assert settings.expose_openapi is False
    assert settings.auth_mode == "oidc"
