from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.schemas import JobCreate
from backend.services import jobs as job_service
from backend.tools.registry import list_tools

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    jobs = await job_service.list_jobs(db)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "tools": list_tools(),
            "title": "Ops Tool-Calling Agent",
        },
    )


@router.post("/ui/jobs")
async def ui_create(goal: str = Form(...), dry_run: str = Form("on"), db: AsyncSession = Depends(get_db)):
    await job_service.create_and_plan(db, JobCreate(goal=goal, dry_run=dry_run == "on"))
    return RedirectResponse("/", status_code=303)


@router.post("/ui/jobs/{job_id}/approve")
async def ui_approve(job_id: str, db: AsyncSession = Depends(get_db)):
    await job_service.approve(db, job_id, actor="ui-operator")
    return RedirectResponse("/", status_code=303)


@router.post("/ui/jobs/{job_id}/run")
async def ui_run(job_id: str, db: AsyncSession = Depends(get_db)):
    await job_service.run_job(db, job_id)
    return RedirectResponse("/", status_code=303)
