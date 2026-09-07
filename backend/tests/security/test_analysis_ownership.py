from app.models.analysis import Analysis
from io import BytesIO
from PIL import Image


def valid_png() -> bytes:
    output = BytesIO()
    Image.new("RGB", (160, 160), (90, 120, 150)).save(output, format="PNG")
    return output.getvalue()


def fake_result() -> dict:
    return {
        "success": True,
        "prediction": "Real",
        "confidence": 92.0,
        "real_probability": 92.0,
        "fake_probability": 8.0,
        "deepfake_type": None,
        "type_confidence": None,
        "risk_level": "Low",
        "model_name": "test-model",
        "model_version": "1",
        "device": "cpu",
        "processing_time": 0.1,
        "face_detected": True,
        "face_count": 1,
        "image_width": 100,
        "image_height": 100,
    }


def test_authenticated_creation_assigns_server_side_owner(security_context, monkeypatch):
    monkeypatch.setattr("app.api.v1.analysis.AIService.analyze_image", lambda *_: fake_result())
    response = security_context.client.post(
        "/api/v1/analysis/image",
        files={"file": ("owned.png", valid_png(), "image/png")},
        headers={**security_context.headers(security_context.user_a), "X-Guest-ID": "forged"},
    )
    assert response.status_code == 200, response.text
    stored = security_context.database.query(Analysis).filter(Analysis.id == response.json()["id"]).one()
    assert stored.owner_user_id == security_context.user_a.id
    assert stored.guest_session_id is None
    assert "file_path" not in response.json()


def test_guest_creation_and_image_analysis_use_verified_guest_owner(security_context, monkeypatch):
    monkeypatch.setattr("app.api.v1.analysis.AIService.analyze_image", lambda *_: fake_result())
    created = security_context.client.post("/api/v1/guest/session")
    assert created.status_code == 201
    repeated = security_context.client.post("/api/v1/guest/session")
    assert repeated.status_code == 201
    response = security_context.client.post(
        "/api/v1/analysis/image",
        files={"file": ("guest.png", valid_png(), "image/png")},
    )
    assert response.status_code == 200, response.text
    stored = security_context.database.query(Analysis).filter(Analysis.id == response.json()["id"]).one()
    assert stored.owner_user_id is None
    assert stored.guest_session_id is not None
    assert "file_path" not in response.json()


def test_failed_inference_releases_usage_and_returns_structured_error(security_context, monkeypatch):
    def fail(*_):
        raise RuntimeError("private internal inference detail")
    monkeypatch.setattr("app.api.v1.analysis.AIService.analyze_image", fail)
    response = security_context.client.post(
        "/api/v1/analysis/image",
        files={"file": ("failure.png", valid_png(), "image/png")},
        headers=security_context.headers(security_context.user_a),
    )
    assert response.status_code == 500
    assert response.json() == {"detail": {"code": "INFERENCE_FAILED", "message": "Image inference failed safely."}}
    from app.models.subscription import DetectionUsage
    usage = security_context.database.query(DetectionUsage).filter(DetectionUsage.identity == security_context.user_a.email).order_by(DetectionUsage.id.desc()).first()
    assert usage.status == "released"
    assert "private internal" not in response.text


def test_model_unavailable_is_safe_503(security_context, monkeypatch):
    from app.ai.model_status import ModelUnavailableError
    def unavailable(*_):
        raise ModelUnavailableError("checkpoint path must stay private")
    monkeypatch.setattr("app.api.v1.analysis.AIService.analyze_image", unavailable)
    response = security_context.client.post(
        "/api/v1/analysis/image",
        files={"file": ("model.png", valid_png(), "image/png")},
        headers=security_context.headers(security_context.user_a),
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "MODEL_UNAVAILABLE"
    assert "checkpoint" not in response.text


def test_history_detail_and_delete_are_owner_scoped(security_context):
    media = security_context.tmp_path / "owned.jpg"
    media.write_bytes(b"owned")
    owned = security_context.create_analysis(security_context.user_a, media)
    legacy = security_context.create_analysis(None, media, filename="legacy.jpg")

    a_history = security_context.client.get("/api/v1/history", headers=security_context.headers(security_context.user_a))
    b_history = security_context.client.get("/api/v1/history", headers=security_context.headers(security_context.user_b))
    assert [item["id"] for item in a_history.json()] == [owned.id]
    assert b_history.json() == []
    assert security_context.client.get(f"/api/v1/history/{owned.id}", headers=security_context.headers(security_context.user_b)).status_code == 404
    assert security_context.client.get(f"/api/v1/history/{legacy.id}", headers=security_context.headers(security_context.user_a)).status_code == 404
    assert security_context.client.delete(f"/api/v1/history/{owned.id}", headers=security_context.headers(security_context.user_b)).status_code == 404
    assert security_context.database.query(Analysis).filter(Analysis.id == owned.id).count() == 1


def test_paginated_me_history_excludes_other_users_and_legacy(security_context):
    media = security_context.tmp_path / "result.jpg"
    media.write_bytes(b"result")
    own = security_context.create_analysis(security_context.user_a, media)
    security_context.create_analysis(security_context.user_b, media)
    security_context.create_analysis(None, media)
    response = security_context.client.get(
        "/api/v1/me/analyses?page=1&page_size=20&source=web&result=Real",
        headers=security_context.headers(security_context.user_a),
    )
    assert response.status_code == 200
    assert response.json()["total_items"] == 1
    assert response.json()["items"][0]["id"] == own.id

    dashboard = security_context.client.get(
        "/api/v1/dashboard/overview",
        headers=security_context.headers(security_context.user_a),
    )
    assert dashboard.status_code == 200
    assert dashboard.json()["totalDetection"] == 1
