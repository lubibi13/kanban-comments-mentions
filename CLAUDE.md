# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project: Kanban with Comments & @Mentions (FastAPI)

## Stack
- FastAPI + SQLModel (ORM) on SQLite, JWT auth via python-jose, password hashing via passlib/bcrypt.
- Python 3.12. Single-user scope (no sharing between users).

## Commands
- Run: `uvicorn app.main:app --reload`  (http://localhost:8000, docs at /docs)
- Test (all): `pytest`
- Test (single): `pytest tests/test_tasks.py::test_register_login_create_and_list_task`
- DB auto-creates at ./app.db on startup via SQLModel.metadata.create_all.

## Layout
- app/main.py — app instance, startup init_db(), router includes
- app/models.py — SQLModel table models AND non-table request/response schemas in one file
- app/db.py — engine + get_session() dependency
- app/config.py — env-var settings (SECRET_KEY, ALGORITHM, token expiry, DATABASE_URL)
- app/auth.py — register/login, JWT, get_current_user dependency
- app/tasks.py — user-scoped CRUD (the authz pattern to copy)
- tests/conftest.py — in-memory SQLite (StaticPool) + get_session override

## Conventions
- Every protected route takes `user: User = Depends(get_current_user)` and filters by `user.id`.
  Ownership checks return 404 (not 403) when the row isn't the caller's. Replicate this for boards/columns/cards.
- New table models MUST be imported (transitively) before metadata.create_all runs, or their tables won't exist in tests.

## Quirks a fresh model would never guess
- **Dependencies are pinned to fix a broken fresh clone: `pydantic==2.9.2`, `bcrypt==4.3.0`. Do NOT upgrade.**
  Newer pydantic breaks SQLModel field annotations; bcrypt 5.x breaks passlib 1.7.4 backend detection.
- `datetime.utcnow` and `@app.on_event("startup")` are deprecated but intentionally kept — don't "fix" them in unrelated commits.
- app.db is a local SQLite file; tests use in-memory so it's irrelevant to the suite (and shouldn't be committed).
