from app.models import Category, Priority
from app.providers.triage.base import TriageResult

URGENT_WORDS = ["flooding", "burst", "fire", "gas leak", "collapse", "electrocut", "sparking"]

# Order matters: the first category with a matching keyword wins.
# "streetlights" must come before "roads" because "street" (a roads keyword)
# is a substring of "streetlight".
CATEGORY_KEYWORDS = {
    Category.water: ["water", "pipe", "burst main", "sewage", "leak"],
    Category.electricity: ["electric", "power", "wire", "transformer", "outage"],
    Category.sanitation: ["garbage", "trash", "sewage", "waste", "sanitation"],
    Category.streetlights: ["streetlight", "street light", "lamp post"],
    Category.roads: ["road", "pothole", "street", "traffic", "sign"],
}


class RuleBasedTriage:
    name = "rules"

    def triage(self, text: str, location: str) -> TriageResult:
        lowered = text.lower()

        category = Category.other
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in lowered for kw in keywords):
                category = cat
                break

        priority = Priority.high if any(w in lowered for w in URGENT_WORDS) else Priority.normal

        summary = text.strip().replace("\n", " ")
        if len(summary) > 140:
            summary = summary[:137] + "..."

        confidence = 0.6 if category != Category.other else 0.3
        return TriageResult(
            category=category,
            priority=priority,
            summary=summary,
            confidence=confidence,
        )