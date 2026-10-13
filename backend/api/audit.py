from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import AuditEvent

router = APIRouter()


@router.get("")
async def list_audit(limit: int = 100, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit))
    rows = [
        {
            "id": e.id,
            "job_id": e.job_id,
            "actor": e.actor,
            "action": e.action,
            "detail": e.detail,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars()
    ]
    return {"events": rows}
