import os
import time

from fastapi import HTTPException, Request

from app.cache import redis_client

WINDOW = 60


def rate_limit(request: Request):
    limit = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))
    ip = request.client.host if request.client else "unknown"
    key = f"rl:{ip}:{int(time.time() // WINDOW)}"
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, WINDOW)
    except Exception:
        return  # Redis down: fail open, never turn a cache outage into a 500
    if count > limit:
        retry_after = WINDOW - int(time.time()) % WINDOW
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )