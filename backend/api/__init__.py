from fastapi import APIRouter

from backend.api import audit, health, jobs, tools, ui

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tools.router, prefix="/api/tools", tags=["tools"])
api_router.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
api_router.include_router(audit.router, prefix="/api/audit", tags=["audit"])
api_router.include_router(ui.router, tags=["ui"])
