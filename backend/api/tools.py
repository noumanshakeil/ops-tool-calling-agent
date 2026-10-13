from fastapi import APIRouter

from backend.tools.registry import list_tools

router = APIRouter()


@router.get("")
async def tools() -> dict:
    return {"tools": list_tools()}
