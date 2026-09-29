# ADR 0002: Frontend Runtime Configuration

## Status
Accepted

## Context
A Vite build bakes `import.meta.env` values into static JavaScript at build time. If the backend API URL were hardcoded into the frontend at build time, the resulting image would be environment-specific, breaking the build-once-deploy-many principle required for the Docker image to work identically across dev, staging, and production.

## Decision
For local development, the frontend calls the backend directly via an absolute URL (`http://localhost:8000`), configured in `src/api.js`. This is acceptable for local development only, where both services run on the same machine with fixed, known ports.

For a production deployment, the correct approach (not yet implemented, given time constraints) is to have nginx proxy `/api` requests through to the backend container, so the frontend's built JavaScript never contains an absolute backend URL — it always calls a relative path, and nginx resolves where that traffic actually goes based on the environment it's deployed in.

## Consequences
- The current setup works correctly for local development and demonstration purposes.
- Deploying this frontend image as-is to any environment other than local Docker Compose (e.g. Kubernetes, a different host) would require rebuilding the image with a different hardcoded URL — which is exactly the "environment-specific image" problem this ADR is meant to flag, not solve.
- The nginx-proxy approach remains the correct fix and is the next planned change to the frontend's Dockerfile and nginx configuration.