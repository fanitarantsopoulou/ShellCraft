def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_disabled_in_production(monkeypatch):
    from fastapi.testclient import TestClient

    from app.core.config import get_settings
    from app.main import create_app

    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    try:
        assert TestClient(create_app()).get("/api/docs").status_code == 404
    finally:
        get_settings.cache_clear()
