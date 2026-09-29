# CivicPulse

An AI-triaged civic complaint system. Citizens submit a complaint, an AI layer
classifies its category and priority (with a deterministic rules-based
fallback if the AI provider fails), and staff work the queue from a
dashboard.

## Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis
- **Frontend:** React + Vite, served by nginx (also proxies `/api` to the backend)
- **AI layer:** pluggable `TriageProvider` interface - rule-based and
  simulated providers included, with automatic fallback and a `rules:fallback`
  audit trail
- **Ops:** Docker Compose (segmented networks, healthchecks, named volumes),
  GitHub Actions CI, Prometheus metrics at `/metrics`

## Running it locally

Requires Docker Desktop.

```bash
git clone https://github.com/humnaattique4-sys/civicpulse.git
cd civicpulse
cp .env.example .env
docker compose up --build
```

Wait for all services to report healthy (`docker compose ps`), then:

```bash
docker compose exec backend python -m app.seed   # optional: 20 sample complaints
```

Open the app at **http://localhost:8080**.

## Useful endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness - no dependencies checked |
| `GET /ready` | Readiness - checks Postgres and Redis, returns 503 and names the failed dependency if either is down |
| `GET /metrics` | Prometheus-format metrics |
| `GET /api/meta/providers` | Active triage provider and last 20 triage outcomes |
| `POST /api/complaints` | Submit a complaint (rate-limited, 10/min per IP by default) |
| `GET /api/complaints` | List complaints, filterable by `category`, `priority`, `status` |
| `GET /api/stats` | Aggregate stats, cached in Redis (see `X-Cache` response header) |

## Running the backend tests

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
pip install -r requirements-dev.txt
python -m pytest --cov=app
```

28 tests, 97%+ coverage, 65% coverage floor enforced in CI.

## Project layout

    backend/   FastAPI app (routes to services to providers, four-layer separation)
    frontend/  React + Vite app
    docs/      ADRs and runbook
    .github/   CI workflow
    compose.yaml, .env.example

## Architecture notes

- **Fallback triage:** if the active provider raises or returns a schema-invalid
  result, the service logs one WARNING and falls back to the rule-based
  provider, recording `triaged_by = "rules:fallback"`. This never surfaces as
  a 500 to the client.
- **Network isolation:** the `backend` service is on both the `edge` and
  `internal` Docker networks; `postgres` and `redis` are on `internal` only
  (`internal: true`, no route to the outside). The `frontend` is on `edge`
  only and cannot reach Postgres or Redis directly.
- **Migrations:** `alembic/env.py` reads `DATABASE_URL` from the environment,
  so the same migration command works locally and inside the `migrate`
  one-shot container.

## Known limitations

- Only rule-based and simulated triage providers are implemented; a real
  LLM-backed provider (Groq/Gemini) is not yet wired in.
- No Kubernetes manifests yet - deployment is Docker Compose only.
- Triage result caching (content-hash keyed) is not yet implemented.

## Team

- Humna Attique ([@humnaattique4-sys](https://github.com/humnaattique4-sys)) - backend, AI layer, Docker/Compose, CI
- Amna ([@Anfey-SE](https://github.com/Anfey-SE)) - frontend, documentation