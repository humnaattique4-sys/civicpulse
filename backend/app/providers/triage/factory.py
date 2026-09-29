import os
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage


def get_provider():
    """Pick the triage provider from the TRIAGE_PROVIDER environment variable.

    Read at call time (not import time) so tests can switch providers.
    Unknown values fall back to the rule-based provider, which never fails.
    """
    choice = os.getenv("TRIAGE_PROVIDER", "rules").lower()
    if choice == "simulated":
        return SimulatedTriage(fail_mode=os.getenv("TRIAGE_FAIL_MODE", "none"))
    if choice in ("llm", "groq"):
        from app.providers.triage.llm import LLMTriage  # lazy: needs openai SDK

        return LLMTriage()
    return RuleBasedTriage()