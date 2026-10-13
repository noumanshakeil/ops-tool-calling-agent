"""Optional seed helper — creates an example record via the service layer."""
import asyncio

from backend.db import SessionLocal, init_db
from backend.schemas import JobCreate
from backend.services import jobs as job_service


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        job = await job_service.create_and_plan(
            session, JobCreate(goal="Seeded demo: healthcheck api then fetch logs", dry_run=True)
        )
        print("seeded", job.id, job.status)


if __name__ == "__main__":
    asyncio.run(main())
