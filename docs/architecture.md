# Architecture

```text
Browser UI ──► FastAPI routers ──► Job service ──► Tool registry
                      │                 │
                      │                 ├── LLM planner (mock/openai/ollama)
                      │                 └── Audit log
                      └── SQLAlchemy (SQLite / Postgres-ready URL)
```

## Control plane flow

1. Operator submits a natural-language **goal**.
2. Planner LLM returns a JSON tool plan + risk.
3. Job enters `pending_approval` (unless approvals disabled).
4. On approve + run, each tool executes with `dry_run` respected.
5. Audit events capture plan/approve/execute/tool outcomes.

## Safety defaults

- `DRY_RUN_DEFAULT=true`
- `REQUIRE_APPROVAL=true`
- High-risk tools (`restart_service`) still run only after approval
