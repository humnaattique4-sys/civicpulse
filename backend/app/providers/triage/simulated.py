from app.models import Category, Priority
from app.providers.triage.base import TriageResult


class SimulatedTriage:
    """Deterministic fake provider for CI. No network, no randomness.

    fail_mode:
      "none"      - returns a valid, deterministic result
      "raise"     - always raises (simulates timeout / 429 / 5xx)
      "malformed" - builds an invalid result (simulates a model returning
                    an out-of-enum category and an oversized summary)
    """

    name = "simulated"

    def __init__(self, fail_mode: str = "none"):
        self.fail_mode = fail_mode

    def triage(self, text: str, location: str) -> TriageResult:
        if self.fail_mode == "raise":
            raise RuntimeError("simulated provider failure")

        if self.fail_mode == "malformed":
            return TriageResult(
                category="not-a-real-category",
                priority="urgent!!",
                summary="x" * 400,
                confidence=5,
            )

        categories = list(Category)
        category = categories[sum(text.encode()) % len(categories)]
        return TriageResult(
            category=category,
            priority=Priority.normal,
            summary=text.strip().replace("\n", " ")[:140],
            confidence=0.5,
        )