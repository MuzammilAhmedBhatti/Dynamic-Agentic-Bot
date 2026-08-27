from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    user_id: uuid.UUID | None
    external_subject: str
    identity_provider: str


@dataclass(frozen=True, slots=True)
class TenantContext:
    organization_id: uuid.UUID
    user_id: uuid.UUID
    membership_id: uuid.UUID
    role_names: frozenset[str]
    permissions: frozenset[str]

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
