from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
)

from app.core.database import Base


class Analysis(Base):

    __tablename__ = "analysis"

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
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )