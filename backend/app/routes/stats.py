import json
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Complaint
from app.cache import redis_client

router = APIRouter(prefix="/api/stats", tags=["stats"])

CACHE_KEY = "stats:aggregate"
CACHE_TTL_SECONDS = 30


@router.get("")
def get_stats(response: Response, db: Session = Depends(get_db)):
    cached = redis_client.get(CACHE_KEY)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return json.loads(cached)

    by_category = dict(
        db.query(Complaint.category, func.count(Complaint.id))
        .group_by(Complaint.category)
        .all()
    )
    by_priority = dict(
        db.query(Complaint.priority, func.count(Complaint.id))
        .group_by(Complaint.priority)
        .all()
    )

    result = {
        "by_category": {k.value: v for k, v in by_category.items()},
        "by_priority": {k.value: v for k, v in by_priority.items()},
    }

    redis_client.setex(CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(result))
    response.headers["X-Cache"] = "MISS"
    return result