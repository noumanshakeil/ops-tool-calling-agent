from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.schemas import ApproveRequest, JobCreate, JobOut, PlanStep
from backend.services import jobs as job_service

router = APIRouter()


def to_out(job) -> JobOut:
    return JobOut(
        id=job.id,
        goal=job.goal,
        status=job.status,
        dry_run=job.dry_run,
        risk=job.risk,
        plan=job_service.parse_plan(job),
        result_summary=job.result_summary,
        created_at=job.created_at,
    )


@router.get("", response_model=list[JobOut])
async def list_jobs(db: AsyncSession = Depends(get_db)) -> list[JobOut]:
    return [to_out(j) for j in await job_service.list_jobs(db)]


@router.post("", response_model=JobOut)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)) -> JobOut:
    job = await job_service.create_and_plan(db, payload)
    return to_out(job)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)) -> JobOut:
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return to_out(job)


@router.post("/{job_id}/approve", response_model=JobOut)
async def approve(job_id: str, body: ApproveRequest, db: AsyncSession = Depends(get_db)) -> JobOut:
    try:
        job = await job_service.approve(db, job_id, body.actor)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return to_out(job)


@router.post("/{job_id}/run", response_model=JobOut)
async def run(job_id: str, db: AsyncSession = Depends(get_db)) -> JobOut:
    try:
        job = await job_service.run_job(db, job_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return to_out(job)
