from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"] = "ready"
    database: Literal["ready"] = "ready"


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str


class TenantContextResponse(BaseModel):
    organization: OrganizationResponse
    user_id: uuid.UUID
    membership_id: uuid.UUID
    roles: list[str]
    permissions: list[str]
