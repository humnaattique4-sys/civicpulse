from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app.cache import redis_client
from app.routes import complaints, stats
from app.logging_config import setup_logging
from app.middleware import RequestIDMiddleware
import app.models

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return {"status": "not ready", "reason": "database unreachable"}, 503

    try:
        redis_client.ping()
    except Exception:
        return {"status": "not ready", "reason": "redis unreachable"}, 503

    return {"status": "ready"}