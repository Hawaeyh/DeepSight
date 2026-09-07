from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class AnalysisFeedback(Base):
    __tablename__ = "analysis_feedback"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    analysis_id = Column(
        Integer,
        ForeignKey("analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_correct = Column(Boolean, nullable=False)
    corrected_prediction = Column(String(20), nullable=True)
    fake_category = Column(String(40), nullable=True)
    manipulation_type = Column(String(100), nullable=True)
    original_file_path = Column(String(500), nullable=True)
    hard_example_path = Column(String(500), nullable=True)
    status = Column(String(30), nullable=False, default="reviewed")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
