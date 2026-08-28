from __future__ import annotations

from functools import lru_cache
from pathlib import Path
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
    oidc_jwks_url: str | None = None
    ai_provider_mode: Literal["managed", "fake"] = "managed"
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    vertex_embedding_location: str | None = None
    vertex_gemini_location: str | None = None
    vertex_embedding_model: str = "gemini-embedding-001"
    vertex_embedding_dimension: int = Field(default=768, ge=128, le=3072)
    vertex_gemini_model: str = "gemini-2.5-flash"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    data_source_encryption_key: str | None = None
    database_query_timeout_ms: int = Field(default=5000, ge=250, le=30000)
    database_query_row_limit: int = Field(default=100, ge=1, le=1000)
    pinecone_api_key: str | None = None
    pinecone_index: str | None = None
    pinecone_index_host: str | None = None
    external_call_timeout_seconds: float = Field(default=30.0, ge=1.0, le=120.0)
    external_call_max_attempts: int = Field(default=3, ge=1, le=5)
    max_pdf_size_mb: int = Field(default=25, ge=1, le=250)
    max_pdf_pages: int = Field(default=200, ge=1, le=2000)
    chunk_size_chars: int = Field(default=1800, ge=200, le=12000)
    chunk_overlap_chars: int = Field(default=240, ge=0, le=2000)
    rag_top_k: int = Field(default=6, ge=1, le=20)
    rag_context_max_chars: int = Field(default=18000, ge=1000, le=100000)
    local_storage_root: Path = Path(".data/objects")

    @property
    def cors_origin_list(self) -> list[str]:
        return _split_csv(self.cors_origins)

    @property
    def allowed_host_list(self) -> list[str]:
        return _split_csv(self.allowed_hosts)

    @property
    def expose_openapi(self) -> bool:
        return self.app_env in {"development", "test"}

    @property
    def max_pdf_size_bytes(self) -> int:
        return self.max_pdf_size_mb * 1024 * 1024

    @property
    def resolved_vertex_embedding_location(self) -> str:
        return self.vertex_embedding_location or self.google_cloud_location

    @property
    def resolved_vertex_gemini_location(self) -> str:
        return self.vertex_gemini_location or self.google_cloud_location

    @property
    def managed_ai_configured(self) -> bool:
        return bool(self.google_cloud_project and self.pinecone_api_key and self.pinecone_index)

    @model_validator(mode="after")
    def validate_security_settings(self) -> Self:
        if not self.database_url.startswith(("postgresql+asyncpg://", "postgresql://")):
            raise ValueError("DATABASE_URL must use PostgreSQL")
        if self.auth_mode == "test" and self.app_env != "test":
            raise ValueError("test authentication is allowed only when APP_ENV=test")
        if self.auth_mode == "oidc" and not (self.oidc_issuer_url and self.oidc_client_id):
            raise ValueError("OIDC_ISSUER_URL and OIDC_CLIENT_ID are required for OIDC")
        if self.ai_provider_mode == "fake" and self.app_env != "test":
            raise ValueError("fake AI providers are allowed only when APP_ENV=test")
        if self.chunk_overlap_chars >= self.chunk_size_chars:
            raise ValueError("CHUNK_OVERLAP_CHARS must be smaller than CHUNK_SIZE_CHARS")
        if self.app_env in {"staging", "production"}:
            if self.auth_mode != "oidc":
                raise ValueError("staging and production require AUTH_MODE=oidc")
            if "*" in self.cors_origin_list or "*" in self.allowed_host_list:
                raise ValueError("wildcard origins and hosts are forbidden outside development")
            if not all(origin.startswith("https://") for origin in self.cors_origin_list):
                raise ValueError("staging and production CORS origins must use HTTPS")
            if self.oidc_issuer_url and not self.oidc_issuer_url.startswith("https://"):
                raise ValueError("OIDC issuer must use HTTPS outside development")
            if not self.data_source_encryption_key:
                raise ValueError("DATA_SOURCE_ENCRYPTION_KEY is required outside local/test use")
        return self


def _split_csv(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise ValueError("comma-separated configuration cannot be empty")
    return items


@lru_cache
def get_settings() -> Settings:
    return Settings()
