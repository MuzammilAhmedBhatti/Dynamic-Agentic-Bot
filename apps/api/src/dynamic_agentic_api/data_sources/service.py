from __future__ import annotations

import base64
import hashlib
import uuid
from dataclasses import dataclass
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from dynamic_agentic_api.config import Settings
from dynamic_agentic_api.data_sources.security import SqlGuard
from dynamic_agentic_api.db.models import DataSource
from dynamic_agentic_api.errors import AppError


@dataclass(frozen=True, slots=True)
class SchemaTable:
    name: str
    columns: list[str]


@dataclass(frozen=True, slots=True)
class DatabaseQueryResult:
    source_id: uuid.UUID
    database_name: str
    tables: list[str]
    columns: list[str]
    rows: list[dict[str, object]]

    @property
    def row_count(self) -> int:
        return len(self.rows)


class CredentialCipher:
    def __init__(self, settings: Settings) -> None:
        key = settings.data_source_encryption_key
        if key is None:
            if settings.app_env not in {"development", "test"}:
                raise AppError(
                    status_code=503,
                    code="CREDENTIAL_ENCRYPTION_UNAVAILABLE",
                    message="Data-source encryption is unavailable.",
                )
            key = base64.urlsafe_b64encode(
                hashlib.sha256(b"dynamic-agentic-local-only").digest()
            ).decode()
        try:
            self._fernet = Fernet(key.encode())
        except (ValueError, TypeError) as exc:
            raise AppError(
                status_code=503,
                code="INVALID_ENCRYPTION_KEY",
                message="Data-source encryption is misconfigured.",
            ) from exc

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except InvalidToken as exc:
            raise AppError(
                status_code=503,
                code="DATA_SOURCE_CREDENTIAL_UNAVAILABLE",
                message="The data-source credential cannot be decrypted.",
            ) from exc


class PostgresConnector:
    def __init__(self, settings: Settings, cipher: CredentialCipher) -> None:
        self._settings = settings
        self._cipher = cipher
        self._guard = SqlGuard(row_limit=settings.database_query_row_limit)

    def validate_connection_url(self, value: str) -> str:
        try:
            url = make_url(value)
        except Exception as exc:
            raise AppError(
                status_code=422,
                code="INVALID_DATA_SOURCE",
                message="The PostgreSQL connection URL is invalid.",
            ) from exc
        if (
            url.drivername not in {"postgresql", "postgresql+asyncpg"}
            or not url.host
            or not url.database
        ):
            raise AppError(
                status_code=422,
                code="INVALID_DATA_SOURCE",
                message="A PostgreSQL database URL is required.",
            )
        return url.set(drivername="postgresql+asyncpg").render_as_string(hide_password=False)

    async def discover_schema(self, source: DataSource) -> list[SchemaTable]:
        rows = await self._execute_raw(
            source,
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = ANY(:tables) "
            "ORDER BY table_name, ordinal_position",
            {"schema": source.allowed_schema, "tables": source.allowed_tables},
            catalog_query=True,
        )
        grouped: dict[str, list[str]] = {}
        for row in rows:
            grouped.setdefault(str(row["table_name"]), []).append(str(row["column_name"]))
        if set(grouped) != set(source.allowed_tables):
            raise AppError(
                status_code=422,
                code="DATA_SOURCE_SCHEMA_MISMATCH",
                message="One or more approved tables do not exist in the approved schema.",
            )
        return [SchemaTable(name, columns) for name, columns in grouped.items()]

    async def execute(self, source: DataSource, statement: str) -> DatabaseQueryResult:
        validated = self._guard.validate(
            statement, allowed_schema=source.allowed_schema, allowed_tables=source.allowed_tables
        )
        rows = await self._execute_raw(source, validated.statement, {})
        columns = list(rows[0].keys()) if rows else []
        database_name = (
            make_url(self._cipher.decrypt(source.encrypted_connection)).database or source.name
        )
        return DatabaseQueryResult(
            source_id=source.id,
            database_name=database_name,
            tables=validated.tables,
            columns=columns,
            rows=[{key: self._json_value(value) for key, value in row.items()} for row in rows],
        )

    async def _execute_raw(
        self,
        source: DataSource,
        statement: str,
        parameters: dict[str, Any],
        *,
        catalog_query: bool = False,
    ) -> list[dict[str, Any]]:
        url = self._cipher.decrypt(source.encrypted_connection)
        engine = create_async_engine(url, pool_pre_ping=True, pool_size=1, max_overflow=0)
        try:
            async with engine.connect() as connection:
                transaction = await connection.begin()
                try:
                    await connection.execute(text("SET TRANSACTION READ ONLY"))
                    await connection.execute(
                        text(
                            "SET LOCAL statement_timeout = "
                            f"{self._settings.database_query_timeout_ms}"
                        )
                    )
                    if not catalog_query:
                        SqlGuard.validate_identifier(source.allowed_schema)
                        await connection.execute(
                            text(f'SET LOCAL search_path = "{source.allowed_schema}"')
                        )
                    result = await connection.execute(text(statement), parameters)
                    rows = [dict(row._mapping) for row in result.fetchall()]
                finally:
                    await transaction.rollback()
            return rows
        except AppError:
            raise
        except Exception as exc:
            raise AppError(
                status_code=503,
                code="DATABASE_QUERY_FAILED",
                message="The approved data source could not complete the read-only query.",
                retryable=True,
            ) from exc
        finally:
            await engine.dispose()

    @staticmethod
    def _json_value(value: object) -> object:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        return str(value)
