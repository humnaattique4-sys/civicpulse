import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
import app.models as _models  # noqa: F401  (registers tables on Base)
from app.routes import complaints, stats


class FakeRedis:
    """In-memory stand-in for Redis so tests need no network."""

    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key, None)

    def ping(self):
        return True


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    fake = FakeRedis()
    monkeypatch.setattr(complaints, "redis_client", fake)
    monkeypatch.setattr(stats, "redis_client", fake)
    monkeypatch.setenv("TRIAGE_PROVIDER", "rules")

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()