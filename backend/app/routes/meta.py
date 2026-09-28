from fastapi import APIRouter

from app.providers.triage.factory import get_provider
from app.services.triage_service import get_recent_outcomes

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/providers")
def providers():
    return {
        "active_provider": get_provider().name,
        "recent_outcomes": get_recent_outcomes(),
    }