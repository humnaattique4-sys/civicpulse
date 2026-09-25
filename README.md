# CivicPulse

Municipal complaint intake, triage, and operations platform. A citizen submits a complaint, an AI (or rule-based fallback) triages it into a category and priority, and it's tracked through a status lifecycle on a live dashboard.

Built for CS4032 - Software Construction and Design, Assignment 1.

## Quickstart

Clone the repo, then from the project root:

```bash
docker compose up --build
```

Wait for `Application startup complete` in the logs. Then seed the database with 30+ realistic complaints:

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # or source venv/bin/activate on Mac/Linux
pip install -r requirements.txt
cd ..
python scripts/seed.py
```

## API

| Method | Path | Behaviour |
|---|---|---|
| POST | `/api/complaints` | Validate → triage → persist. Returns 201. |
| GET | `/api/complaints/{id}` | 200 / 404 |
| GET | `/api/complaints` | Filter by category, priority, status; paginated |
| PATCH | `/api/complaints/{id}/status` | Enforces status state machine. Invalid transition → 409 |
| GET | `/api/stats` | Aggregate counts, Redis-cached (30s TTL), `X-Cache` header |
| GET | `/health` | Liveness — never touches the database |
| GET | `/ready` | Readiness — checks Postgres and Redis |

Full interactive API docs: `http://localhost:8000/docs`

## Architecture

- **Backend**: FastAPI + SQLAlchemy, four-layer structure (routes → services → repositories → providers)
- **Database**: PostgreSQL 16, tables created on startup (Alembic migrations planned)
- **Cache**: Redis 7 — read-through cache for `/api/stats` and (planned) rate limiting
- **AI Triage**: Rule-based keyword classifier (`RuleBasedTriage`), designed behind a `TriageProvider` interface so an LLM-backed provider can be swapped in without changing the API contract

## Status

Backend, AI triage, caching, and CI are implemented and tested. Frontend and Kubernetes deployment are in progress.