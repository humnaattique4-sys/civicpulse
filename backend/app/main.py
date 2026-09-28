from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import engine
from app.cache import redis_client
from app.routes import complaints, stats
from app.logging_config import setup_logging
from app.middleware import RequestIDMiddleware
import app.models

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="CivicPulse", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)

app.include_router(complaints.router)
app.include_router(stats.router)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for e in exc.errors():
        field = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
        errors[field] = e["msg"]
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    failed = []

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        failed.append("postgres")

    try:
        redis_client.ping()
    except Exception:
        failed.append("redis")

    if failed:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "failed": failed},
        )
    return {"status": "ready"}