# AI Usage Disclosure

Per section 5.5 of the assignment brief: honest attribution, not avoidance.

## Tool used

Claude (Anthropic), via the claude.ai chat interface, for the entire
backend AI-layer, testing, Docker/Compose, CI, and documentation work on
this repository.

## What Claude wrote or shaped

- **Triage provider interface and implementations**
  (`backend/app/providers/triage/base.py`, `rules.py`, `simulated.py`,
  `factory.py`) and the fallback logic in
  `backend/app/services/triage_service.py`. Claude wrote the initial code;
  I ran it, hit a real bug in the test fixture, reported the failure, and
  Claude fixed it before I accepted the code.
- **Backend test suite** (`backend/tests/`), 28 tests total, written by
  Claude, run and verified locally by me at each step before committing.
- **Rate limiter, `/ready` 503 fix, 400 field-level errors,
  `/api/meta/providers`, `/metrics`** — Claude wrote each, I applied the
  edits, ran the tests myself, and reported failures back (e.g. an
  indentation error I introduced while pasting, a missing import) which
  Claude then corrected.
- **Dockerfiles, `compose.yaml`, `.dockerignore`, `.env.example`** —
  written by Claude. I ran every build and `docker compose up` myself and
  reported the actual errors (a `ModuleNotFoundError` for
  `prometheus-client`, a stale Postgres volume with an old password, a
  `useradd` ordering bug in the Dockerfile) which Claude diagnosed from
  the logs I pasted and fixed.
- **`alembic/env.py` fix** so migrations read `DATABASE_URL` from the
  environment instead of only `alembic.ini` — written by Claude after I
  pasted the original file.
- **CI workflow** (`.github/workflows/ci.yml`) — written by Claude.
- **Seed script** (`backend/app/seed.py`) — written by Claude.
- **README.md and this engineering-notes document
  (`docs/ENGINEERING-NOTES.md`)** — drafted by Claude from the actual
  commands, logs, and code in this repository; I reviewed and pasted them
  in myself.

## What I changed or decided myself

- Which items to prioritize under time pressure (backend AI layer and
  tests first, then Docker, then docs; Kubernetes and the real LLM
  provider deferred and disclosed as not-yet-implemented rather than
  faked).
- Freed disk space and moved Docker's data directory to a second drive
  to get local builds working at all.
- Split remaining work with my teammate and reviewed/closed a duplicate
  PR (#2) that overlapped with a fix I had already pushed directly.
- Every command in this repository's history was run by me, on my own
  machine; I read the output and decided whether to proceed, retry, or
  ask for a different fix rather than pasting code without checking it.

## Why this approach

I do not yet have enough experience to write a working four-layer FastAPI
backend, a correct multi-stage Dockerfile, and a segmented-network Compose
stack from scratch in the time available. Using Claude let me get a
working, tested system built while I read every file, ran every command
myself, and fixed real environment problems (missing dependencies, stale
volumes, disk space) that Claude could not see directly. I can explain
why the fallback logs a WARNING instead of raising, why the networks are
split the way they are, and where the gaps are (Kubernetes, real LLM
provider, triage caching), because I was the one running and debugging
the code at every step.

- Frontend tests (409 message, filters, pagination, X-Cache badge, error boundary) and small accessibility labels on the Dashboard selects. I read, ran and tested this code before committing it.