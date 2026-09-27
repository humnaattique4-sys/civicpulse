# Engineering Notes

## 1. Three things that differ between laptop and CI runner, and the exact line that freezes each

1. **Python version.** My laptop has Python 3.14 installed locally, but the actual runtime is pinned in `backend/Dockerfile`: `FROM python:3.12-slim`. This line guarantees the code always runs on 3.12 regardless of what's on the developer's machine — this distinction mattered directly, since a local `pip install` on 3.14 failed to build `pydantic-core` from source (no pre-built wheel existed yet for that Python version), while the Docker build on 3.12 succeeded immediately using a pre-built wheel.
2. **Database availability.** My laptop has a long-lived Postgres container with existing data; the CI runner has none. This is frozen by `.github/workflows/ci.yml`'s `test-backend` job, which does not start a database at all — this is exactly what surfaced the bug where `app/main.py` originally tried to create tables at *import time*, which failed with no database present. Fixed by moving that logic into a FastAPI `lifespan` startup hook instead.
3. **Installed system tools.** My laptop has whatever Rust/build tools happen to be present (or absent) from unrelated installs; the CI runner has a clean, minimal Ubuntu image. This is frozen by the `requirements.txt` file itself combined with `actions/setup-python@v5` pinning the exact Python version — dependencies are resolved fresh, from pinned or loosely-pinned versions in that file, with no reliance on anything already present on a machine.

## 2. Where the pipeline sits on the CI/CD maturity ladder

The current pipeline (`ci.yml`) runs on every push to `dev`, installs dependencies, and verifies the app imports and runs successfully — this is closer to the "Basic CI" rung: automated build/verify on every push, but not yet full test coverage, not yet automated deployment. There is no `cd.yml` implemented yet, so nothing is automatically built, pushed to a registry, or deployed — that would be the next rung up ("Continuous Delivery"), and it buys the team the ability to know, at any moment, that the latest `dev` commit is not just import-clean but actually deployable, with a human only needed to approve the promotion to `main`.

## 3. The exact line guaranteeing build-once-deploy-many, and what breaks without it

The backend's `Dockerfile` reads configuration only from environment variables at container start (see `app/database.py`: `DATABASE_URL = os.getenv("DATABASE_URL", ...)` and `app/cache.py`: `REDIS_URL = os.getenv("REDIS_URL", ...)`) rather than baking any environment-specific value into the image at build time. Without this, the same built image could not be pointed at a different database or Redis instance without rebuilding it — defeating the entire purpose of building an image once and deploying it across dev/staging/production.

The frontend does **not** yet fully satisfy this guarantee — as documented in ADR 0002, the current frontend calls a hardcoded `http://localhost:8000` in `src/api.js`, which means the built frontend image is only valid for local development. This is a known, documented gap rather than an oversight.

## 4. With a live LLM provider, the service is probabilistic — how was CI kept deterministic?

The current implementation only ships `RuleBasedTriage` (see `app/services/triage_service.py`), which is fully deterministic keyword matching with no external network calls at all — "correct" for this component currently means: given the same input text, the same category/priority/summary are returned every time, and this is exactly what makes it safe to run in CI with zero flakiness. If an LLM-backed provider were added later, "correct" would need to shift from exact-output matching to schema-conformance and safety checks (does the response validate against the Pydantic schema? does it fall back correctly on timeout/error?), with CI pinned to a deterministic fake provider (`SimulatedTriage`, not yet implemented) rather than testing against the real probabilistic model directly.

## 5. HPA lag

Not applicable — Kubernetes deployment, HPA, and the associated load testing were not implemented in this submission due to time constraints, prioritized against the assignment's own stated guidance that AI layer, backend, and CI/CD matter more than Kubernetes when time is short (§5.1).

## 6. Why VPA would run in Off mode

Not implemented for the same reason as above. Conceptually: VPA in Auto mode adjusting CPU requests while HPA scales on CPU utilization creates a feedback loop — VPA raising a pod's request lowers computed utilization (usage ÷ request), which causes HPA to scale in, raising per-pod load, which causes VPA to raise the request again. Recommender-only mode avoids this by requiring a human to review and apply changes rather than the two controllers reacting to each other automatically.

## 7. Where does the internal-only network leave a service calling a hosted LLM?

This was directly relevant even without Kubernetes: in `docker-compose.yaml`, `postgres` and `redis` are only reachable from `backend` on the same Docker network as `backend` itself (the current single-network setup does not yet implement the two-network split the assignment describes in §3.2). If a hosted LLM provider were added, the service making that outbound call would need to remain on a network with a route to the internet — meaning the strict internal-only isolation described in the assignment (where database/cache containers have zero internet route) is compatible with an LLM-calling service only if that specific service sits on a network bridge that both reaches the internal services *and* has outbound internet access, which is exactly the role `backend` already plays in the current setup.

## 8. The failure that cost more than an hour

Getting WSL2 and Docker Desktop working on Windows took over an hour by itself: `wsl --install` repeatedly stalled at 0% downloading Ubuntu, which I first believed was just a slow connection. The command that revealed the actual cause was `wsl --status`, which showed the WSL2 platform was present but the kernel file itself was missing ("The WSL 2 kernel file is not found") — the automated `wsl --update` command hung the same way, which told me the issue was a network path being blocked specifically for Microsoft Store/CDN downloads, not a general connectivity problem. The fix was downloading the kernel package directly via a browser from `aka.ms/wsl2kernel` and installing it manually, sidestepping whatever was blocking the automated path entirely.