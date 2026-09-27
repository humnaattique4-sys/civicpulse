# AI Usage Disclosure

## Tools used
Claude (Anthropic) was used extensively throughout this project's development.

## What it helped with
- Scaffolding the initial repository structure and four-layer backend architecture (routes/services/repositories/providers)
- Writing the FastAPI routes, SQLAlchemy models, Pydantic schemas, and the rule-based triage service
- Debugging environment setup issues (WSL2/Docker installation on Windows, Python 3.14 package compatibility)
- Debugging runtime issues: a CORS misconfiguration between frontend and backend, an incorrectly generated (empty) Alembic migration, and a database driver mismatch (psycopg vs psycopg2)
- Writing the Docker Compose configuration, Dockerfiles, and GitHub Actions CI workflow
- Writing documentation: README, ADRs, this file, and the engineering notes
- Scaffolding the React frontend (Submit and Dashboard views) and connecting it to the backend API

## What was reviewed and changed
Every piece of generated code was run and tested against the actual running system before being accepted — nothing was copied in without verification. Several real bugs were caught this way and fixed with further AI assistance, notably:
- A category-classification bug where "streetlight" was being matched by the "roads" keyword list before reaching the "streetlights" list, due to dictionary ordering — fixed by reordering the keyword checks.
- An Alembic migration that was silently empty (no actual `CREATE TABLE`) because it was generated against a database that already had the table from leftover auto-create code — fixed by resetting the migration history and regenerating against a genuinely fresh database.

## Attribution stance
Per course policy, specific disclosure carries no penalty. This project would not have been completed to this scope within the available time without AI assistance, and that assistance is disclosed here in full rather than obscured.