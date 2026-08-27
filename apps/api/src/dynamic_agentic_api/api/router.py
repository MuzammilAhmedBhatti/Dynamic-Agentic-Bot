from __future__ import annotations

from fastapi import APIRouter

from dynamic_agentic_api.api.health import router as health_router
from dynamic_agentic_api.api.organizations import router as organizations_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(organizations_router)
