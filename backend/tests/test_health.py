from fastapi.testclient import TestClient
import pytest


def test_health_response_contains_no_secrets(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert payload == {
        "status": "ok",
        "environment": "testing",
        "database": "ok",
        "models": {
            "binary": "disabled",
            "multiclass": "disabled",
            "face_detector": "disabled",
        },
        "version": "1.0.0",
    }
    serialized = response.text.lower()
    for forbidden in ("secret", "password", "database_url", "firebase_credentials"):
        assert forbidden not in serialized


def test_health_degrades_safely_when_database_is_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unavailable() -> None:
        raise ConnectionError("postgresql+psycopg://user:password@private/database")

    monkeypatch.setattr("app.api.v1.health.check_database_connection", unavailable)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["database"] == "unavailable"
    assert "password" not in response.text.lower()
