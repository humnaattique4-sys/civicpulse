from fastapi import FastAPI
from app.database import engine, Base
from app.routes import complaints, stats
import app.models  # ensures models are registered before create_all

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CivicPulse")

app.include_router(complaints.router)
app.include_router(stats.router)

@app.get("/health")
def health():
    return {"status": "ok"}