from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String
from app.core.database import Base


class ExtensionVideoSession(Base):
    __tablename__ = "extension_video_sessions"
    __table_args__ = (Index("ix_extension_video_sessions_owner_user_id", "owner_user_id"), Index("ix_extension_video_sessions_status", "status"))
    id = Column(String(36), primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    usage_reservation_key = Column(String(64), nullable=True)
    selected_model_id = Column(String(80), nullable=False)
    actual_model_id = Column(String(80), nullable=True)
    page_domain = Column(String(253), nullable=False)
    status = Column(String(24), nullable=False, default="analysing")
    frames_received = Column(Integer, nullable=False, default=0)
    frames_analysed = Column(Integer, nullable=False, default=0)
    frames_skipped = Column(Integer, nullable=False, default=0)
    suspicious_frames = Column(Integer, nullable=False, default=0)
    predictions = Column(JSON, nullable=True)
    overall_result = Column(String(32), nullable=True)
    overall_confidence = Column(Float, nullable=True)
    failure_code = Column(String(40), nullable=True)
    analysis_id = Column(Integer, ForeignKey("analysis.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
