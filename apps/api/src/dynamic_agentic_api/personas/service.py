from __future__ import annotations

import uuid
from dataclasses import dataclass

from dynamic_agentic_api.errors import AppError

_NAMESPACE = uuid.UUID("d4f86048-9e39-4f85-b62d-62abdb8fb251")


@dataclass(frozen=True, slots=True)
class PersonaDefinition:
    id: uuid.UUID
    slug: str
    name: str
    description: str
    system_behavior: str
    allowed_routes: tuple[str, ...]
    default_provider: str
    default_model: str
    scope: str = "system"
    is_active: bool = True


class PersonaRegistry:
    def __init__(self, *, default_provider: str, default_model: str) -> None:
        common_routes = ("document", "database", "math")
        self._personas = {
            item.slug: item
            for item in (
                PersonaDefinition(
                    id=uuid.uuid5(_NAMESPACE, "general-assistant"),
                    slug="general-assistant",
                    name="General Assistant",
                    description="General-purpose grounded document and data assistant.",
                    system_behavior=(
                        "Be concise, evidence-led, and explicit when authorized data is "
                        "insufficient."
                    ),
                    allowed_routes=common_routes,
                    default_provider=default_provider,
                    default_model=default_model,
                ),
                PersonaDefinition(
                    id=uuid.uuid5(_NAMESPACE, "financial-analyst"),
                    slug="financial-analyst",
                    name="Financial Analyst",
                    description=(
                        "Analyzes authorized financial data using deterministic calculations."
                    ),
                    system_behavior=(
                        "Explain financial results precisely and never invent inputs or perform "
                        "hidden arithmetic."
                    ),
                    allowed_routes=common_routes,
                    default_provider=default_provider,
                    default_model=default_model,
                ),
                PersonaDefinition(
                    id=uuid.uuid5(_NAMESPACE, "legal-advisor"),
                    slug="legal-advisor",
                    name="Legal Advisor",
                    description=(
                        "Explains authorized legal documents without presenting legal advice as "
                        "fact."
                    ),
                    system_behavior=(
                        "Ground legal explanations in cited evidence and state that output is "
                        "informational."
                    ),
                    allowed_routes=("document",),
                    default_provider=default_provider,
                    default_model=default_model,
                ),
            )
        }
        self._by_id = {item.id: item for item in self._personas.values()}

    def list_active(self) -> list[PersonaDefinition]:
        return list(self._personas.values())

    def get_by_slug(self, slug: str) -> PersonaDefinition:
        persona = self._personas.get(slug)
        if persona is None or not persona.is_active:
            raise AppError(
                status_code=422,
                code="INVALID_PERSONA",
                message="The selected persona is unavailable.",
            )
        return persona

    def get_by_id(self, persona_id: uuid.UUID) -> PersonaDefinition:
        persona = self._by_id.get(persona_id)
        if persona is None or not persona.is_active:
            raise AppError(
                status_code=422,
                code="INVALID_PERSONA",
                message="The selected persona is unavailable.",
            )
        return persona
