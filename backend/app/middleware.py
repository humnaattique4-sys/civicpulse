import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("civicpulse")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code}",
            extra={"request_id": request_id},
        )
        return response