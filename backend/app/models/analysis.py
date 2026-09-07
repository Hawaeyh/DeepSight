from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    JSON,
)

from app.core.database import Base
from app.core.config import settings


class Analysis(Base):

    __tablename__ = "analysis"
    __table_args__ = (
        CheckConstraint(
            "NOT (owner_user_id IS NOT NULL AND guest_session_id IS NOT NULL)",
            name="analysis_single_owner",
        ),
        Index("ix_analysis_owner_user_id_created_at", "owner_user_id", "created_at"),
    )

    # ==========================================================
    # Primary Key
    # ==========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # File Information
    # ==========================================================

    filename = Column(
        String(255),
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    file_type = Column(
        String(20),           # Image / Video
        nullable=False,
        index=True,
    )

    file_extension = Column(
        String(10),
        nullable=True,
    )

    file_size = Column(
        Float,                # MB
        nullable=True,
    )

    # ==========================================================
    # AI Detection Result
    # ==========================================================

    prediction = Column(
        String(20),           # Real / Fake
        nullable=False,
        index=True,
    )

    confidence = Column(
        Float,
        nullable=False,
    )

    real_probability = Column(
        Float,
        nullable=True,
    )

    fake_probability = Column(
        Float,
        nullable=True,
    )

    # ==========================================================
    # Deepfake Classification
    # ==========================================================

    deepfake_type = Column(
        String(100),
        nullable=True,
    )

    type_confidence = Column(
        Float,
        nullable=True,
    )

    # ==========================================================
    # Face Detection
    # ==========================================================

    face_detected = Column(
        Boolean,
        default=False,
    )

    face_count = Column(
        Integer,
        default=0,
    )

    # ==========================================================
    # Image Information
    # ==========================================================

    image_width = Column(
        Integer,
        nullable=True,
    )

    image_height = Column(
        Integer,
        nullable=True,
    )

    # ==========================================================
    # Video Information
    # ==========================================================

    video_duration = Column(
        Float,
        nullable=True,
    )

    frames_analyzed = Column(
        Integer,
        nullable=True,
    )

    fake_frames = Column(
        Integer,
        nullable=True,
    )

    real_frames = Column(
        Integer,
        nullable=True,
    )

    # ==========================================================
    # Detection Metadata
    # ==========================================================

    risk_level = Column(
        String(20),
        nullable=False,
    )

    model_name = Column(
        String(100),
        nullable=False,
        default="EfficientNet-B0",
        index=True,
    )

    model_version = Column(
        String(100),
        nullable=False,
    )

    device = Column(
        String(20),
        nullable=False,
    )

    processing_time = Column(
        Float,
        nullable=False,
    )

    # ==========================================================
    # User Verification (Future Feature)
    # ==========================================================

    verified_result = Column(
        String(20),
        nullable=True,
    )

    remarks = Column(
        String(500),
        nullable=True,
    )

    # ==========================================================
    # Status
    # ==========================================================

    status = Column(
        String(20),
        nullable=False,
        default="Completed",
    )

    # ==========================================================
    # Timestamp
    # ==========================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @property
    def result(self) -> str:
        if self.confidence < settings.IMAGE_INCONCLUSIVE_THRESHOLD:
            return "inconclusive"
        return "likely_real" if self.prediction == "Real" else "likely_manipulated"

    @property
    def display_label(self) -> str:
        return {
            "likely_real": "Likely Real",
            "likely_manipulated": "Likely Manipulated",
            "inconclusive": "Inconclusive",
        }[self.result]

    owner_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    guest_session_id = Column(
        Integer,
        ForeignKey("guest_sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    source = Column(String(40), nullable=True, default="web", index=True)
    quality_metadata = Column(JSON, nullable=True)
    quality_warnings = Column(JSON, nullable=True)
    selected_face_index = Column(Integer, nullable=True)
    selected_face_box = Column(JSON, nullable=True)
    face_detection_confidence = Column(Float, nullable=True)
