from __future__ import annotations

from fastapi import APIRouter

from dynamic_agentic_api.api.auth import router as auth_router
from dynamic_agentic_api.api.chat import router as chat_router
from dynamic_agentic_api.api.health import router as health_router
from dynamic_agentic_api.api.intelligence import router as intelligence_router
from dynamic_agentic_api.api.knowledge import router as knowledge_router
from dynamic_agentic_api.api.organizations import router as organizations_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(knowledge_router)
api_router.include_router(chat_router)
api_router.include_router(intelligence_router)
