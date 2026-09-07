from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String

from app.core.database import Base


class WebcamSession(Base):
    __tablename__ = "webcam_sessions"

    id = Column(String(36), primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    usage_reservation_key = Column(String(64), nullable=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    valid_frame_count = Column(Integer, nullable=False, default=0)
    predictions = Column(JSON, nullable=True)
    final_result = Column(String(32), nullable=True)
    final_confidence = Column(Float, nullable=True)
    analysis_id = Column(Integer, ForeignKey("analysis.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
