from __future__ import annotations

from dataclasses import dataclass

from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.llm.gateway import LlmProvider


@dataclass(frozen=True, slots=True)
class ProviderModel:
    provider: str
    model: str
    available: bool
    reason: str | None = None


class LlmRegistry:
    def __init__(self, providers: list[LlmProvider], catalog: list[ProviderModel]) -> None:
        self._providers = {
            (provider.provider_name, provider.model): provider for provider in providers
        }
        self._catalog = catalog

    def list_models(self) -> list[ProviderModel]:
        return self._catalog

    def resolve(self, provider: str | None, model: str | None) -> LlmProvider:
        available = [item for item in self._catalog if item.available]
        choice: ProviderModel | None
        if provider is None and model is None:
            if not available:
                raise AppError(
                    status_code=503,
                    code="LLM_PROVIDER_UNAVAILABLE",
                    message="No language model provider is available.",
                )
            choice = available[0]
        elif provider is None or model is None:
            raise AppError(
                status_code=422,
                code="INVALID_MODEL_SELECTION",
                message="Provider and model must be selected together.",
            )
        else:
            choice = next(
                (
                    item
                    for item in self._catalog
                    if item.provider == provider and item.model == model
                ),
                None,
            )
            if choice is None:
                raise AppError(
                    status_code=422,
                    code="INVALID_MODEL_SELECTION",
                    message="The selected provider/model is not allowlisted.",
                )
            if not choice.available:
                raise AppError(
                    status_code=503,
                    code="LLM_PROVIDER_UNAVAILABLE",
                    message=choice.reason or "The selected provider is unavailable.",
                )
        return self._providers[(choice.provider, choice.model)]
