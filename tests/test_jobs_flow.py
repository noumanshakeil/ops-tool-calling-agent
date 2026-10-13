import pytest


@pytest.mark.asyncio
async def test_plan_approve_run(client):
    created = await client.post("/api/jobs", json={"goal": "Check api health then fetch logs", "dry_run": True})
    assert created.status_code == 200
    job = created.json()
    assert job["status"] == "pending_approval"
    assert len(job["plan"]) >= 1

    approved = await client.post(f"/api/jobs/{job['id']}/approve", json={"actor": "tester"})
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    ran = await client.post(f"/api/jobs/{job['id']}/run")
    assert ran.status_code == 200
    assert ran.json()["status"] == "succeeded"

    audit = await client.get("/api/audit")
    assert audit.status_code == 200
    assert len(audit.json()["events"]) >= 3
