"""Builtin ops tools. Each tool is sandboxed / simulated for local safety."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


ToolFn = Callable[[dict[str, Any], bool], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risk: str  # low | medium | high
    fn: ToolFn


async def run_healthcheck(args: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    target = args.get("target", "unknown")
    if dry_run:
        return {"ok": True, "dry_run": True, "target": target, "would": "GET /health"}
    await asyncio.sleep(0.05)
    return {"ok": True, "target": target, "latency_ms": 42, "status": "healthy"}


async def fetch_logs(args: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    target = args.get("target", "unknown")
    lines = int(args.get("lines", 50))
    sample = [f"{target} log line {i}" for i in range(1, min(lines, 5) + 1)]
    if dry_run:
        return {"ok": True, "dry_run": True, "target": target, "lines": lines}
    return {"ok": True, "target": target, "lines": sample}


async def restart_service(args: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    target = args.get("target", "unknown")
    if dry_run:
        return {"ok": True, "dry_run": True, "target": target, "would": "kubectl rollout restart"}
    await asyncio.sleep(0.1)
    return {"ok": True, "target": target, "restarted": True}


async def scale_replicas(args: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    target = args.get("target", "unknown")
    replicas = int(args.get("replicas", 2))
    if dry_run:
        return {"ok": True, "dry_run": True, "target": target, "replicas": replicas}
    return {"ok": True, "target": target, "replicas": replicas, "applied": True}


REGISTRY: dict[str, ToolSpec] = {
    "run_healthcheck": ToolSpec("run_healthcheck", "Probe service health", "low", run_healthcheck),
    "fetch_logs": ToolSpec("fetch_logs", "Fetch recent logs", "low", fetch_logs),
    "restart_service": ToolSpec("restart_service", "Restart a service", "high", restart_service),
    "scale_replicas": ToolSpec("scale_replicas", "Scale deployment replicas", "medium", scale_replicas),
}


def list_tools() -> list[dict[str, str]]:
    return [
        {"name": t.name, "description": t.description, "risk": t.risk}
        for t in REGISTRY.values()
    ]


async def execute(tool: str, args: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    if tool not in REGISTRY:
        return {"ok": False, "error": f"unknown tool: {tool}"}
    return await REGISTRY[tool].fn(args, dry_run)


def dump_args(args: dict[str, Any]) -> str:
    return json.dumps(args, sort_keys=True)
