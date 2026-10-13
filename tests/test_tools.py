import pytest

from backend.tools.registry import execute, list_tools


def test_registry_not_empty():
    assert len(list_tools()) >= 4


@pytest.mark.asyncio
async def test_healthcheck_dry_run():
    result = await execute("run_healthcheck", {"target": "api"}, dry_run=True)
    assert result["ok"] is True
    assert result["dry_run"] is True
