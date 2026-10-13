import time

import pytest


@pytest.mark.asyncio
async def test_list_jobs_latency(client):
    started = time.perf_counter()
    for _ in range(20):
        r = await client.get("/api/jobs")
        assert r.status_code == 200
    elapsed = time.perf_counter() - started
    # Generous CI-friendly budget for 20 sequential calls.
    assert elapsed < 5.0
