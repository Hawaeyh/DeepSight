from app.models.notification import Notification
from app.models.subscription import AccountEntitlement, DetectionUsage, SubscriptionPlan
from app.services.subscription_service import SubscriptionService
from app.services.stripe_service import StripeService
from types import SimpleNamespace


def test_health_reports_disabled_external_services_without_secrets(security_context):
    payments = security_context.client.get("/api/v1/health/payments")
    firebase = security_context.client.get("/api/v1/health/firebase")
    assert payments.json()["status"] == "not_configured"
    assert firebase.json()["status"] == "not_configured"
    assert "X-Content-Type-Options" in payments.headers
    assert "secret" not in payments.text.lower()


def test_plans_are_database_backed_and_usage_can_be_released(security_context):
    response = security_context.client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200
    assert security_context.database.query(SubscriptionPlan).count() == 4
    usage = SubscriptionService.reserve(security_context.database, None, "guest-test", "image")
    assert usage.status == "reserved"
    SubscriptionService.release(security_context.database, usage)
    assert usage.status == "released"


def test_notifications_are_owner_scoped(security_context):
    security_context.database.add_all([
        Notification(user_id=security_context.user_a.id, category="video_completed", title="Ready", message="A video is ready."),
        Notification(user_id=security_context.user_b.id, category="video_failed", title="Failed", message="A video failed."),
    ])
    security_context.database.commit()
    response = security_context.client.get("/api/v1/notifications", headers=security_context.headers(security_context.user_a))
    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Ready"]
    item_id = response.json()[0]["id"]
    assert security_context.client.patch(f"/api/v1/notifications/{item_id}/read", headers=security_context.headers(security_context.user_b)).status_code == 404


def test_disabled_stripe_and_firebase_fail_safely(security_context):
    checkout = security_context.client.post("/api/v1/subscriptions/checkout", json={"plan_code": "basic", "billing_period": "monthly"}, headers=security_context.headers(security_context.user_a))
    firebase = security_context.client.post("/api/v1/auth/firebase", json={"id_token": "x" * 30})
    assert checkout.status_code == 503 and checkout.json()["detail"]["status"] == "not_configured"
    assert firebase.status_code == 503 and firebase.json()["detail"]["status"] == "not_configured"


def test_admin_monitoring_uses_database_role(security_context):
    assert security_context.client.get("/api/v1/admin/overview", headers=security_context.headers(security_context.user_a)).status_code == 403
    security_context.user_a.role = "admin"; security_context.database.commit()
    response = security_context.client.get("/api/v1/admin/overview", headers=security_context.headers(security_context.user_a))
    assert response.status_code == 200
    assert response.json()["totalUsers"] == 2


def test_admin_analysis_history_includes_owned_guest_and_legacy(security_context):
    from app.models.guest_session import GuestSession
    security_context.user_a.role = "admin"
    guest = GuestSession(token_hash="admin-history-guest", expires_at=__import__("datetime").datetime.utcnow() + __import__("datetime").timedelta(hours=1))
    security_context.database.add(guest); security_context.database.commit(); security_context.database.refresh(guest)
    media = security_context.tmp_path / "admin-history.jpg"; media.write_bytes(b"test")
    security_context.create_analysis(security_context.user_a, media)
    security_context.create_analysis(None, media, guest_session_id=guest.id)
    security_context.create_analysis(None, media)
    response = security_context.client.get("/api/v1/admin/analyses?page_size=100", headers=security_context.headers(security_context.user_a))
    assert response.status_code == 200, response.text
    ownership = {item["ownershipType"] for item in response.json()["items"]}
    assert {"owned", "guest", "legacy"} <= ownership
    assert all("file_path" not in item for item in response.json()["items"])
    assert security_context.client.get("/api/v1/admin/analyses", headers=security_context.headers(security_context.user_b)).status_code == 403


def test_analysis_metadata_converts_numpy_values(security_context):
    import numpy as np
    from app.services.analysis_service import AnalysisService
    saved = AnalysisService.save(
        db=security_context.database, filename="native.png", file_path="private/native.png", file_type="Image",
        prediction="Real", confidence=np.float32(90), real_probability=np.float64(90), fake_probability=np.float32(10),
        risk_level="Low", model_name="test", model_version="1", device="cpu", processing_time=np.float32(0.1),
        owner_user_id=security_context.user_a.id, quality_metadata={"score": np.float32(1.5)},
        quality_warnings=["ok"], selected_face_index=np.int64(0), selected_face_box=np.array([1, 2, 3, 4]),
        face_detection_confidence=np.float32(0.9),
    )
    assert saved.quality_metadata == {"score": 1.5}
    assert saved.selected_face_box == [1, 2, 3, 4]


def test_webcam_session_reserves_and_releases_usage_when_empty(security_context):
    entitlement = SubscriptionService.ensure_entitlement(security_context.database, security_context.user_a.email, security_context.user_a.id)
    entitlement.plan = "lite"; security_context.database.commit()
    created = security_context.client.post("/api/v1/webcam/sessions", headers=security_context.headers(security_context.user_a))
    assert created.status_code == 201, created.text
    stopped = security_context.client.post(f"/api/v1/webcam/sessions/{created.json()['sessionId']}/stop", headers=security_context.headers(security_context.user_a))
    assert stopped.json()["status"] == "cancelled"
    usage = security_context.database.query(DetectionUsage).filter(DetectionUsage.identity == security_context.user_a.email, DetectionUsage.media_type == "webcam").one()
    assert usage.status == "released"


def test_extension_video_frames_require_authenticated_identity(security_context):
    response = security_context.client.post("/api/v1/extension/videos/frames", data={"page_domain": "example.com"}, files={"file": ("frame.jpg", b"invalid", "image/jpeg")})
    assert response.status_code == 401


def test_mocked_firebase_identity_creates_unique_local_user(security_context, monkeypatch):
    monkeypatch.setattr("app.api.v1.auth.verify_firebase_token", lambda _: {"uid": "firebase-unique", "email": "firebase@example.com", "email_verified": True, "name": "Firebase User"})
    response = security_context.client.post("/api/v1/auth/firebase", json={"id_token": "valid-mocked-token-value-123"})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "user"
    assert response.json()["user"]["firebase_uid"] == "firebase-unique"


def test_firebase_does_not_silently_link_existing_email(security_context, monkeypatch):
    monkeypatch.setattr("app.api.v1.auth.verify_firebase_token", lambda _: {"uid": "different-uid", "email": security_context.user_a.email, "email_verified": True})
    response = security_context.client.post("/api/v1/auth/firebase", json={"id_token": "valid-mocked-token-value-456"})
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "ACCOUNT_LINK_CONFLICT"


def test_verified_stripe_event_is_idempotent_and_updates_subscription(security_context):
    plan = security_context.database.query(SubscriptionPlan).filter(SubscriptionPlan.code == "basic").one()
    plan.stripe_monthly_price_id = "price_basic_monthly_test"
    security_context.database.commit()
    event = {"id": "evt_test_unique", "type": "customer.subscription.updated", "livemode": False, "data": {"object": {"id": "sub_test", "customer": "cus_test", "status": "active", "cancel_at_period_end": False, "current_period_end": 1893456000, "items": {"data": [{"price": {"id": "price_basic_monthly_test", "recurring": {"interval": "month"}}}]}, "metadata": {"user_id": str(security_context.user_a.id)}}}}
    first = StripeService.process_event(security_context.database, event)
    second = StripeService.process_event(security_context.database, event)
    entitlement = security_context.database.query(AccountEntitlement).filter(AccountEntitlement.user_id == security_context.user_a.id).one()
    assert first["status"] == "processed" and second["status"] == "duplicate"
    assert entitlement.plan == "basic" and entitlement.stripe_customer_id == "cus_test"


def test_checkout_uses_database_price_and_reuses_customer(security_context, monkeypatch):
    plan = security_context.database.query(SubscriptionPlan).filter(SubscriptionPlan.code == "basic").one()
    plan.stripe_monthly_price_id = "price_database_monthly"
    entitlement = SubscriptionService.ensure_entitlement(security_context.database, security_context.user_a.email, security_context.user_a.id)
    entitlement.stripe_customer_id = "cus_existing"
    security_context.database.commit()
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(url="https://checkout.stripe.test/session", id="cs_test")

    fake = SimpleNamespace(checkout=SimpleNamespace(Session=SimpleNamespace(create=create)))
    monkeypatch.setattr(StripeService, "client", staticmethod(lambda: fake))
    monkeypatch.setattr(StripeService, "sync_configured_prices", staticmethod(lambda _db: None))
    result = StripeService.checkout(security_context.database, security_context.user_a, "basic", "monthly")
    assert result["checkoutUrl"].startswith("https://checkout.stripe.test/")
    assert captured["line_items"] == [{"price": "price_database_monthly", "quantity": 1}]
    assert captured["customer"] == "cus_existing"
    assert "customer_email" not in captured


def test_checkout_annual_uses_only_approved_database_price(security_context, monkeypatch):
    plan = security_context.database.query(SubscriptionPlan).filter(SubscriptionPlan.code == "basic").one()
    plan.stripe_annual_price_id = "price_database_annual"
    security_context.database.commit()
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(url="https://checkout.stripe.test/annual", id="cs_annual")

    fake = SimpleNamespace(checkout=SimpleNamespace(Session=SimpleNamespace(create=create)))
    monkeypatch.setattr(StripeService, "client", staticmethod(lambda: fake))
    monkeypatch.setattr(StripeService, "sync_configured_prices", staticmethod(lambda _db: None))
    StripeService.checkout(security_context.database, security_context.user_a, "basic", "annual")
    assert captured["line_items"][0]["price"] == "price_database_annual"
    response = security_context.client.post("/api/v1/subscriptions/checkout", json={"plan_code": "basic", "billing_period": "monthly", "price_id": "price_attacker"}, headers=security_context.headers(security_context.user_a))
    assert response.status_code == 422
