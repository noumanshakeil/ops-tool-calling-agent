# HTTP API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + LLM mode |
| GET | `/api/tools` | Registered tools |
| GET | `/api/jobs` | List jobs |
| POST | `/api/jobs` | Create + plan `{goal, dry_run?}` |
| GET | `/api/jobs/{id}` | Job detail |
| POST | `/api/jobs/{id}/approve` | Approve plan |
| POST | `/api/jobs/{id}/run` | Execute plan |
| GET | `/api/audit` | Recent audit events |

Interactive docs: `/docs`
