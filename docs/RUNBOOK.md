# CivicPulse Runbook

## Deploying

**Local (Docker Compose):**
```bash
docker compose up --build
```
Wait for `Application startup complete` in the backend logs. Apply database migrations if the schema changed:
```bash
cd backend
alembic upgrade head
```

**Seeding data:**
```bash
python scripts/seed.py
```
Safe to run multiple times — it checks existing complaint count and skips if already seeded.

## Rolling back

**If a bad code change is deployed:**
```bash
docker compose down
git checkout <previous-commit-or-tag>
docker compose up --build
```

**If a bad database migration is applied:**
```bash
cd backend
alembic downgrade -1
```
This reverts the most recent migration by one step.

## Reading logs

Logs are structured JSON, written to stdout, and viewable via:
```bash
docker compose logs backend --tail 50
docker compose logs backend -f   # follow live
```
Every log line includes a `request_id` field, propagated from the `X-Request-ID` header (or generated if absent), so a single request can be traced across log lines.

## What to do when triage starts failing

1. Check logs for `WARNING` entries mentioning `triaged_by: rules:fallback` — this indicates the primary triage path failed and the system fell back correctly. This is expected, safe behavior, not an outage.
2. Check `docker compose logs backend` for repeated errors from the triage service specifically.
3. Currently the only implemented provider is `RuleBasedTriage`, which is fully local and deterministic — it does not depend on any external service, so "triage failing" in the current build most likely means a bug in the keyword logic (e.g. the streetlight/road category collision we fixed during development), not an external outage.
4. Confirm the fix with a manual test: `POST /api/complaints` with a known input and check the returned `category`/`priority` match expectations.

## Health checks

- `GET /health` — liveness only, never touches the database. If this fails, the process itself is down.
- `GET /ready` — readiness, checks both Postgres and Redis connectivity. If this fails but `/health` passes, a dependency (not the app) is the problem — check `docker ps` to confirm Postgres/Redis containers are running.