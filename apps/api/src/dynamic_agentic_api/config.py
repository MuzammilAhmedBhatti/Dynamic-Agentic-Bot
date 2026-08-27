from __future__ import annotations

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        validate_default=True,
    )

    app_name: str = "Dynamic Agentic Bot API"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = Field(default="", min_length=1)
    cors_origins: str = "http://localhost:3000"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    auth_mode: Literal["disabled", "test", "oidc"] = "disabled"
    oidc_issuer_url: str | None = None
    oidc_client_id: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return _split_csv(self.cors_origins)

    @property
    def allowed_host_list(self) -> list[str]:
        return _split_csv(self.allowed_hosts)

    @property
    def expose_openapi(self) -> bool:
        return self.app_env in {"development", "test"}

    @model_validator(mode="after")
    def validate_security_settings(self) -> Self:
        if not self.database_url.startswith(("postgresql+asyncpg://", "postgresql://")):
            raise ValueError("DATABASE_URL must use PostgreSQL")
        if self.auth_mode == "test" and self.app_env != "test":
            raise ValueError("test authentication is allowed only when APP_ENV=test")
        if self.auth_mode == "oidc" and not (self.oidc_issuer_url and self.oidc_client_id):
            raise ValueError("OIDC_ISSUER_URL and OIDC_CLIENT_ID are required for OIDC")
        if self.app_env in {"staging", "production"}:
            if self.auth_mode != "oidc":
                raise ValueError("staging and production require AUTH_MODE=oidc")
            if "*" in self.cors_origin_list or "*" in self.allowed_host_list:
                raise ValueError("wildcard origins and hosts are forbidden outside development")
            if not all(origin.startswith("https://") for origin in self.cors_origin_list):
                raise ValueError("staging and production CORS origins must use HTTPS")
            if self.oidc_issuer_url and not self.oidc_issuer_url.startswith("https://"):
                raise ValueError("OIDC issuer must use HTTPS outside development")
        return self


def _split_csv(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise ValueError("comma-separated configuration cannot be empty")
    return items


@lru_cache
def get_settings() -> Settings:
    return Settings()
