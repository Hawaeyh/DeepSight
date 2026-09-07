from pathlib import Path

from app.core.paths import IMAGE_UPLOAD_DIR


def test_public_media_is_removed_and_owner_media_is_protected(security_context):
    IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    media = IMAGE_UPLOAD_DIR / "private-test.jpg"
    media.write_bytes(b"private-media")
    analysis = security_context.create_analysis(security_context.user_a, media)

    assert security_context.client.get(f"/media/images/{media.name}").status_code == 404
    endpoint = f"/api/v1/analyses/{analysis.id}/media/original"
    owner = security_context.client.get(endpoint, headers=security_context.headers(security_context.user_a))
    assert owner.status_code == 200
    assert owner.content == b"private-media"
    assert owner.headers["cache-control"] == "private, no-store"
    assert security_context.client.get(endpoint, headers=security_context.headers(security_context.user_b)).status_code == 404


def test_stored_path_outside_upload_root_is_rejected(security_context):
    outside = security_context.tmp_path / "outside.jpg"
    outside.write_bytes(b"must-not-leak")
    analysis = security_context.create_analysis(security_context.user_a, outside)
    response = security_context.client.get(
        f"/api/v1/analyses/{analysis.id}/media/original",
        headers=security_context.headers(security_context.user_a),
    )
    assert response.status_code == 404
    assert b"must-not-leak" not in response.content


def test_report_and_feedback_are_owner_scoped(security_context):
    media = security_context.tmp_path / "feedback.jpg"
    media.write_bytes(b"feedback")
    analysis = security_context.create_analysis(security_context.user_a, media)
    report_url = f"/api/v1/reports/{analysis.id}"
    assert security_context.client.get(report_url, headers=security_context.headers(security_context.user_b)).status_code == 404
    owner_report = security_context.client.get(report_url, headers=security_context.headers(security_context.user_a))
    assert owner_report.status_code == 200
    assert owner_report.headers["content-type"] == "application/pdf"

    payload = {"analysis_id": analysis.id, "is_correct": True}
    assert security_context.client.post("/api/v1/feedback", json=payload, headers=security_context.headers(security_context.user_b)).status_code == 404
    accepted = security_context.client.post("/api/v1/feedback", json=payload, headers=security_context.headers(security_context.user_a))
    assert accepted.status_code == 200
    feedback = analysis.feedback if hasattr(analysis, "feedback") else None
    stored = security_context.database.execute(
        __import__("sqlalchemy").text("SELECT owner_user_id FROM analysis_feedback WHERE analysis_id=:id"),
        {"id": analysis.id},
    ).scalar_one()
    assert feedback is None
    assert stored == security_context.user_a.id
