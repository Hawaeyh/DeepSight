from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, text

from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    code = Column(String(20), primary_key=True)
    name = Column(String(80), nullable=False)
    monthly_price = Column(Float, nullable=False, default=0)
    annual_price = Column(Float, nullable=False, default=0)
    image_limit = Column(Integer, nullable=True)
    video_limit = Column(Integer, nullable=True)
    webcam_limit = Column(Integer, nullable=True)
    extension_limit = Column(Integer, nullable=True)
    window_hours = Column(Integer, nullable=True)
    history_retention_days = Column(Integer, nullable=True)
    report_enabled = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    features = Column(JSON, nullable=True)
    stripe_monthly_price_id = Column(String(120), nullable=True, unique=True)
    stripe_annual_price_id = Column(String(120), nullable=True, unique=True)


class AccountEntitlement(Base):
    __tablename__ = "account_entitlements"
    __table_args__ = (Index("ix_account_entitlements_user_id", "user_id"),)

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True)
    plan = Column(String(20), nullable=False, default="starter")
    status = Column(String(20), nullable=False, default="active")
    stripe_customer_id = Column(String(120), nullable=True, unique=True)
    stripe_subscription_id = Column(String(120), nullable=True, unique=True)
    billing_interval = Column(String(20), nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    stripe_price_id = Column(String(120), nullable=True)
    provider = Column(String(20), nullable=False, default="local", server_default="local")
    cancel_at_period_end = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DetectionUsage(Base):
    __tablename__ = "detection_usage"
    __table_args__ = (Index("ix_detection_usage_reservation_key", "reservation_key"),)

    id = Column(Integer, primary_key=True, index=True)
    identity = Column(String(255), nullable=False, index=True)
    media_type = Column(String(20), nullable=False)
    reservation_key = Column(String(64), nullable=True, unique=True)
    status = Column(String(20), nullable=False, default="completed", server_default="completed", index=True)
    completed_at = Column(DateTime, nullable=True)
    released_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class StripeEvent(Base):
    __tablename__ = "stripe_events"
    __table_args__ = (Index("ix_stripe_events_event_id", "event_id"),)

    id = Column(Integer, primary_key=True)
    event_id = Column(String(120), nullable=False, unique=True)
    event_type = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="processed")
    customer_id = Column(String(120), nullable=True)
    subscription_id = Column(String(120), nullable=True)
    safe_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
