from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""


class JobCreate(BaseModel):
    goal: str = Field(min_length=3, max_length=4000)
    dry_run: bool | None = None


class JobOut(BaseModel):
    id: str
    goal: str
    status: str
    dry_run: bool
    risk: str
    plan: list[PlanStep]
    result_summary: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    actor: str = "operator"


class HealthOut(BaseModel):
    status: str
    service: str
    version: str
    llm_mode: str
