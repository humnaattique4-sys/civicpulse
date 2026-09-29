from app import main as main_module

VALID = {"text": "Burst water main flooding Street 12 since fajr", "location": "Street 12"}


class DeadEngine:
    def connect(self):
        raise ConnectionError("db down")


class OkEngine:
    def connect(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, *args):
        pass


class DeadRedis:
    def ping(self):
        raise ConnectionError("redis down")


def test_health_does_not_need_any_dependency(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_failing_provider_still_returns_201_with_fallback(client, monkeypatch):
    monkeypatch.setenv("TRIAGE_PROVIDER", "simulated")
    monkeypatch.setenv("TRIAGE_FAIL_MODE", "raise")
    response = client.post("/api/complaints", json=VALID)
    assert response.status_code == 201
    assert response.json()["triaged_by"] == "rules:fallback"


def test_create_then_get_complaint(client):
    created = client.post("/api/complaints", json=VALID).json()
    assert created["category"] == "water"
    assert created["priority"] == "high"
    assert created["status"] == "open"
    fetched = client.get(f"/api/complaints/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


def test_get_unknown_complaint_is_404(client):
    response = client.get("/api/complaints/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_invalid_status_transition_is_409(client):
    created = client.post("/api/complaints", json=VALID).json()
    response = client.patch(f"/api/complaints/{created['id']}/status", json={"status": "resolved"})
    assert response.status_code == 409
    assert "Invalid transition" in response.json()["detail"]


def test_valid_status_transition_succeeds(client):
    created = client.post("/api/complaints", json=VALID).json()
    response = client.patch(f"/api/complaints/{created['id']}/status", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_stats_miss_then_hit_then_invalidated_by_new_complaint(client):
    client.post("/api/complaints", json=VALID)
    first = client.get("/api/stats")
    assert first.headers["x-cache"] == "MISS"
    second = client.get("/api/stats")
    assert second.headers["x-cache"] == "HIT"
    client.post("/api/complaints", json=VALID)
    third = client.get("/api/stats")
    assert third.headers["x-cache"] == "MISS"
    assert third.json()["by_category"]["water"] == 2


def test_list_complaints_filters_by_category(client):
    client.post("/api/complaints", json=VALID)
    client.post("/api/complaints", json={"text": "Garbage not collected for five days", "location": "I-8"})
    response = client.get("/api/complaints?category=sanitation")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "sanitation"


def test_rate_limit_returns_429_with_retry_after(client, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "2")
    client.post("/api/complaints", json=VALID)
    client.post("/api/complaints", json=VALID)
    third = client.post("/api/complaints", json=VALID)
    assert third.status_code == 429
    assert "retry-after" in third.headers


def test_ready_is_503_and_names_postgres_when_db_down(client, monkeypatch):
    monkeypatch.setattr(main_module, "engine", DeadEngine())
    response = client.get("/ready")
    assert response.status_code == 503
    assert "postgres" in response.json()["failed"]


def test_ready_is_503_and_names_redis_when_redis_down(client, monkeypatch):
    monkeypatch.setattr(main_module, "engine", OkEngine())
    monkeypatch.setattr(main_module, "redis_client", DeadRedis())
    response = client.get("/ready")
    assert response.status_code == 503
    assert "redis" in response.json()["failed"]


def test_validation_error_is_400_with_field_errors(client):
    response = client.post("/api/complaints", json={"text": "short", "location": "x"})
    assert response.status_code == 400
    assert "text" in response.json()["errors"]


def test_meta_providers_reports_active_provider_and_outcomes(client):
    client.post("/api/complaints", json=VALID)
    response = client.get("/api/meta/providers")
    assert response.status_code == 200
    body = response.json()
    assert body["active_provider"] == "rules"
    assert len(body["recent_outcomes"]) >= 1
    assert set(body["recent_outcomes"][0]) == {"provider", "latency_ms", "fallback"}


def test_metrics_endpoint_exposes_prometheus_text(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text