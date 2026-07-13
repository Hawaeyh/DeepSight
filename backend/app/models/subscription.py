from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class AccountEntitlement(Base):
    __tablename__ = "account_entitlements"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    plan = Column(String(20), nullable=False, default="starter")
    status = Column(String(20), nullable=False, default="active")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DetectionUsage(Base):
    __tablename__ = "detection_usage"

    id = Column(Integer, primary_key=True, index=True)
    identity = Column(String(255), nullable=False, index=True)
    media_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
