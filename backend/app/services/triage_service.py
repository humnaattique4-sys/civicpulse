import logging
import time
from collections import deque

from app.providers.triage.factory import get_provider
from app.providers.triage.rules import RuleBasedTriage

logger = logging.getLogger("civicpulse")

# Last 20 triage outcomes, kept in memory for /api/meta/providers.
_recent_outcomes = deque(maxlen=20)


def get_recent_outcomes():
    return list(_recent_outcomes)


def run_triage(text: str, location: str, provider=None):
    """Triage a complaint. Never raises because a provider failed.

    If the chosen provider raises or returns something that fails schema
    validation, we log one WARNING and fall back to the rule-based provider,
    recording triaged_by = "rules:fallback".
    """
    provider = provider or get_provider()
    start = time.perf_counter()
    fallback = False

    try:
        result = provider.triage(text, location)
        triaged_by = provider.name
    except Exception as exc:
        logger.warning(
            f"triage fallback: provider={provider.name} error={type(exc).__name__}"
        )
        result = RuleBasedTriage().triage(text, location)
        triaged_by = "rules:fallback"
        fallback = True

    latency_ms = int((time.perf_counter() - start) * 1000)
    _recent_outcomes.append(
        {"provider": triaged_by, "latency_ms": latency_ms, "fallback": fallback}
    )
    return result.category, result.priority, result.summary, triaged_by, latency_ms