import time
from app.models import Category, Priority

URGENT_WORDS = ["flooding", "burst", "fire", "gas leak", "collapse", "electrocut", "sparking"]

CATEGORY_KEYWORDS = {
    Category.water: ["water", "pipe", "burst main", "sewage", "leak"],
    Category.electricity: ["electric", "power", "wire", "transformer", "outage"],
    Category.sanitation: ["garbage", "trash", "sewage", "waste", "sanitation"],
    Category.streetlights: ["streetlight", "street light", "lamp post"],
    Category.roads: ["road", "pothole", "street", "traffic", "sign"],
}


def run_triage(text: str, location: str):
    start = time.perf_counter()
    lowered = text.lower()

    category = Category.other
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            category = cat
            break

    priority = Priority.high if any(w in lowered for w in URGENT_WORDS) else Priority.normal

    summary = text.strip().replace("\n", " ")[:137]
    if len(text) > 137:
        summary += "..."

    latency_ms = int((time.perf_counter() - start) * 1000)
    return category, priority, summary, "rules", latency_ms