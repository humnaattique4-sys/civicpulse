# Engineering Notes

## 1. Three things that differ between my laptop and a CI runner, and what freezes each

- **OS and Python version.** My laptop runs Windows with Python 3.14. CI and
  the container both use `python:3.12-slim`, pinned in `backend/Dockerfile`
  line 1: `FROM python:3.12-slim AS builder`. This is also pinned by digest
  via the base image's resolved SHA that Docker records at build time, so a
  Debian security update to `slim` doesn't silently change my build.
- **Installed packages.** Locally I had `prometheus-client` in my venv but
  not in `backend/requirements.txt`, so the app ran fine on my machine and
  crashed on start in the container (`ModuleNotFoundError: No module named
  'prometheus_client'`). `backend/requirements-dev.txt` line 1
  (`-r requirements.txt`) plus `requirements.txt` itself is what freezes the
  dependency set for CI and Docker; a package only in my local venv is
  invisible to both.
- **Database and cache.** My laptop can fall back to whatever Postgres/Redis
  happen to be running locally (or none, if I haven't started them). CI and
  Docker Compose both start fresh, disposable services:
  `compose.yaml` pins `postgres:16-alpine` and `redis:7-alpine` by tag, and
  `tests/conftest.py` uses an in-memory SQLite engine
  (`create_engine("sqlite://", ...)`) plus a `FakeRedis` stand-in, so tests
  never depend on whatever state is on my machine.

## 2. Where the pipeline sits on the CI/CD maturity ladder

Our pipeline (`.github/workflows/ci.yml`) runs on every PR into `main` and
every push to `dev`: it installs dependencies, runs the 28-test backend
suite with a 65% coverage gate (`--cov-fail-under=65`), and runs the
frontend's Vitest suite. That's automated build + automated test on every
change, which is continuous integration proper — not just "we have a CI
badge."

We are not at continuous deployment: there's no `cd.yml`, nothing builds or
pushes a versioned image automatically, and nothing deploys on merge. We're
sitting at what the lecture calls the "automated testing" rung, one below
"automated deployment to staging."

The next rung up would add a `cd.yml` gated by `needs: [test-backend,
test-frontend]`, which builds and tags the Docker images by commit SHA and
pushes them to a registry on merge to `main`. That buys us a guarantee that
whatever passed CI is exactly what gets deployed, with no manual rebuild
step in between where something could drift.

## 3. The exact line guaranteeing build-once-deploy-many, and what breaks without it

We don't have this yet. Our images are tagged `:latest` by default from
`docker compose build` (no explicit tag in `compose.yaml`), which is the
opposite of build-once-deploy-many: `:latest` means "whatever was built
most recently," so two people running `docker compose up --build` on
different commits get different images under the same name, and a
redeploy can silently pick up unintended code.

The fix, not yet implemented: build the image once per commit, tag it with
the commit SHA (e.g. `civicpulse-backend:${GITHUB_SHA}`), push it, and
have every environment reference that exact tag rather than `:latest`.
Without it, "it worked in staging" doesn't guarantee "it's the same
artifact in production" — that's the −8 deduction category for deploying
`:latest` anywhere.

## 4. Probabilistic correctness with a live LLM provider

**Not yet implemented.** We have not wired in a real LLM-backed
`TriageProvider` (only `RuleBasedTriage` and `SimulatedTriage` in
`backend/app/providers/triage/`). Once added, "correct" for that component
can't mean "identical output every run" the way `test_rules_burst_water_
main_is_water_and_high` in `tests/test_triage.py` does for the rule-based
provider. It would instead mean the response validates against the
`TriageResult` schema (`backend/app/providers/triage/base.py`) and the
category is plausible for the input, checked with a permissive assertion
(e.g. category is not `other` for an obviously water-related complaint)
rather than an exact match.

To keep CI deterministic, `app/providers/triage/factory.py` reads the
provider choice from the `TRIAGE_PROVIDER` environment variable at call
time, and `.github/workflows/ci.yml` pins `TRIAGE_PROVIDER: simulated`.
CI never calls a real network provider, so it never depends on model
non-determinism, rate limits, or an API key.

## 5. HPA lag

**Not yet implemented.** We have no Kubernetes manifests and no HPA
configured, so there's no lag to measure. This is planned as follow-up
work; the compose-only setup documented in the README is what currently
exists.

## 6. Why VPA is in Off mode

**Not yet implemented.** No VPA is configured, for the same reason as (5).

## 7. The `internal: true` network and a hosted LLM call

Our `compose.yaml` defines two networks: `edge` (default bridge) and
`internal` (`driver: bridge`, `internal: true`, meaning Docker gives it no
route out to the host or internet). `postgres` and `redis` are attached to
`internal` only. If `backend` were also `internal`-only, it could reach the
database but could never make an outbound HTTPS call to a hosted LLM API.

We resolved this by putting `backend` on **both** networks:
`networks: [edge, internal]` in the `backend` service. `edge` gives it a
route out to the internet (for the LLM call, once added), and `internal`
gives it a route to Postgres and Redis. `frontend` is `edge`-only, so it
can reach `backend` but has no route to `postgres` or `redis` at all —
verified with `docker compose exec frontend sh -c "nc -zv -w 2 postgres
5432"`, which fails to resolve the hostname, versus the same check from
`backend`, which succeeds.

## 8. The failure

The backend container crashed on startup with `ModuleNotFoundError: No
module named 'prometheus_client'`, even though the exact same code ran
fine with `python -m pytest` and `uvicorn app.main:app --reload` on my own
machine. I first assumed it was a Docker networking or healthcheck timing
issue, since the failure only showed up as `backend-1 is unhealthy` in
`docker compose ps` and I'd just changed the compose healthchecks. I spent
time rewriting the Dockerfile's `USER` and `HEALTHCHECK` lines before
looking at the actual container log.

`docker compose logs backend --tail 40` was the command that told me the
truth: it printed the full Python traceback ending in
`ModuleNotFoundError: No module named 'prometheus_client'`. I had installed
`prometheus-client` into my local venv with `pip install prometheus-client`
while building `app/metrics.py`, but never added it to
`backend/requirements.txt` — so my venv had it, but the Docker image, built
strictly from `requirements.txt`, did not. The fix was one line added to
`requirements.txt`, followed by `docker compose build --no-cache backend
migrate`.