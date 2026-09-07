from datetime import datetime, timedelta

from app.models.guest_session import GuestSession

from .test_analysis_ownership import fake_result, valid_png


def test_server_guest_session_owns_result_and_other_guest_is_denied(security_context, monkeypatch):
    monkeypatch.setattr("app.api.v1.analysis.AIService.analyze_image", lambda *_: fake_result())
    guest_a = security_context.client
    created_session = guest_a.post("/api/v1/guest/session")
    assert created_session.status_code == 201
    assert "httponly" in created_session.headers["set-cookie"].lower()
    created = guest_a.post(
        "/api/v1/analysis/image",
        files={"file": ("guest.png", valid_png(), "image/png")},
        headers={"X-Guest-ID": "browser-forgery"},
    )
    assert created.status_code == 200, created.text
    analysis_id = created.json()["id"]
    assert guest_a.get(f"/api/v1/analysis/{analysis_id}").status_code == 200

    from app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as guest_b:
        assert guest_b.post("/api/v1/guest/session").status_code == 201
        assert guest_b.get(f"/api/v1/analysis/{analysis_id}").status_code == 404


def test_forged_guest_header_is_ignored_and_expired_cookie_is_denied(security_context):
    from app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        denied = client.get("/api/v1/analysis/1", headers={"X-Guest-ID": "forged"})
        assert denied.status_code == 401
        assert client.post("/api/v1/guest/session").status_code == 201
        session = security_context.database.query(GuestSession).order_by(GuestSession.id.desc()).first()
        session.expires_at = datetime.utcnow() - timedelta(seconds=1)
        security_context.database.commit()
        assert client.get("/api/v1/analysis/1").status_code == 401


def test_guest_records_transfer_only_with_verified_cookie(security_context, monkeypatch):
    monkeypatch.setattr("app.api.v1.analysis.AIService.analyze_image", lambda *_: fake_result())
    client = security_context.client
    assert client.post("/api/v1/guest/session").status_code == 201
    created = client.post(
        "/api/v1/analysis/image",
        files={"file": ("transfer.png", valid_png(), "image/png")},
    )
    analysis_id = created.json()["id"]
    transferred = client.post(
        "/api/v1/guest/transfer",
        headers=security_context.headers(security_context.user_a),
    )
    assert transferred.status_code == 200
    assert transferred.json()["transferred"] == 1
    from app.models.analysis import Analysis

    analysis = security_context.database.query(Analysis).filter(Analysis.id == analysis_id).one()
    security_context.database.refresh(analysis)
    assert analysis.owner_user_id == security_context.user_a.id
    assert analysis.guest_session_id is None
