"""Job planning, approval, and execution orchestration."""
from __future__ import annotations

import json
import uuid
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.llm import get_llm
from backend.models import AuditEvent, Job, ToolRun
from backend.schemas import JobCreate, PlanStep
from backend.tools.registry import execute, list_tools

log = structlog.get_logger(__name__)


async def audit(session: AsyncSession, *, job_id: str | None, action: str, detail: str, actor: str = "system") -> None:
    session.add(AuditEvent(job_id=job_id, action=action, detail=detail, actor=actor))


async def create_and_plan(session: AsyncSession, payload: JobCreate) -> Job:
    dry_run = settings.dry_run_default if payload.dry_run is None else payload.dry_run
    job = Job(
        id=uuid.uuid4().hex[:12],
        goal=payload.goal.strip(),
        status="planning",
        dry_run=dry_run,
    )
    session.add(job)
    await session.flush()

    llm = get_llm()
    tool_catalog = json.dumps(list_tools())
    prompt = (
        "Create a minimal safe ops plan as JSON with keys plan (list of "
        "{tool,args,rationale}), risk (low|medium|high), summary.\n"
        f"Available tools: {tool_catalog}\n"
        f"Goal: {job.goal}"
    )
    plan_data = await llm.complete_json(
        prompt,
        system="You are a careful SRE co-pilot. Prefer healthchecks before mutations.",
    )
    steps = plan_data.get("plan") or []
    job.plan_json = json.dumps(steps)
    job.risk = str(plan_data.get("risk") or "medium")
    job.result_summary = str(plan_data.get("summary") or "")
    job.status = "pending_approval" if settings.require_approval else "approved"
    await audit(session, job_id=job.id, action="planned", detail=job.plan_json)
    await session.commit()
    await session.refresh(job)
    log.info("job_planned", job_id=job.id, risk=job.risk, steps=len(steps))
    return job


def parse_plan(job: Job) -> list[PlanStep]:
    raw = json.loads(job.plan_json or "[]")
    return [PlanStep.model_validate(x) for x in raw]


async def get_job(session: AsyncSession, job_id: str) -> Job | None:
    result = await session.execute(
        select(Job).options(selectinload(Job.runs), selectinload(Job.audits)).where(Job.id == job_id)
    )
    return result.scalar_one_or_none()


async def list_jobs(session: AsyncSession, limit: int = 50) -> list[Job]:
    result = await session.execute(select(Job).order_by(Job.created_at.desc()).limit(limit))
    return list(result.scalars())


async def approve(session: AsyncSession, job_id: str, actor: str) -> Job:
    job = await get_job(session, job_id)
    if not job:
        raise ValueError("job not found")
    if job.status not in {"pending_approval", "approved"}:
        raise ValueError(f"cannot approve from status={job.status}")
    job.status = "approved"
    await audit(session, job_id=job.id, action="approved", detail="operator approved plan", actor=actor)
    await session.commit()
    await session.refresh(job)
    return job


async def run_job(session: AsyncSession, job_id: str) -> Job:
    job = await get_job(session, job_id)
    if not job:
        raise ValueError("job not found")
    if settings.require_approval and job.status != "approved":
        raise ValueError("job must be approved before execution")
    job.status = "running"
    await audit(session, job_id=job.id, action="execute_start", detail=f"dry_run={job.dry_run}")
    await session.commit()

    outputs: list[dict[str, Any]] = []
    for step in parse_plan(job):
        run = ToolRun(job_id=job.id, tool=step.tool, args_json=json.dumps(step.args), status="running")
        session.add(run)
        await session.flush()
        result = await execute(step.tool, step.args, dry_run=job.dry_run)
        run.status = "succeeded" if result.get("ok") else "failed"
        run.output = json.dumps(result)
        outputs.append({"tool": step.tool, "result": result})
        await audit(
            session,
            job_id=job.id,
            action="tool_run",
            detail=f"{step.tool} -> {run.status}",
        )
        if not result.get("ok"):
            job.status = "failed"
            job.result_summary = json.dumps(outputs, indent=2)
            await session.commit()
            await session.refresh(job)
            return job

    job.status = "succeeded"
    job.result_summary = json.dumps(outputs, indent=2)
    await audit(session, job_id=job.id, action="execute_done", detail="all tools ok")
    await session.commit()
    await session.refresh(job)
    return job
