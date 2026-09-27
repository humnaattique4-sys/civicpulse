# ADR 0003: Deploy by Commit SHA, Never by Tag

## Status
Accepted

## Context
The CI pipeline builds Docker images on every push. If deployments reference a mutable tag like `:latest`, the question "what is production actually running?" has no reliable answer — `:latest` can point to a different image at different times, and there is no way to trace a running container back to the exact source code that produced it.

## Decision
Every image built by the CI/CD pipeline is tagged with the immutable commit SHA it was built from (`civicpulse-backend:${GITHUB_SHA}`). Deployments reference this SHA-tagged image explicitly, never `:latest`. `:latest` may still be pushed to the registry for convenience/browsing, but it is never the tag used in an actual deployment manifest or `docker compose` reference.

## Consequences
- "What is production running?" always has a one-word answer: the commit SHA, which can be pasted directly into `git show` to see the exact code.
- Rolling back is unambiguous — redeploying a previous SHA-tagged image is guaranteed to restore the exact previous behavior, with no risk of `:latest` having moved on to a newer, different image in the meantime.
- The trade-off is a small amount of extra bookkeeping (tracking which SHA is "current" in each environment), which is a worthwhile cost for the debugging and audit clarity it buys, especially during an incident when "what changed?" needs a fast, certain answer.