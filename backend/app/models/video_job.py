from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text

from app.core.database import Base


class VideoJob(Base):
    __tablename__ = "video_jobs"
    __table_args__ = (Index("ix_video_jobs_analysis_id", "analysis_id"),)

    id = Column(String(36), primary_key=True)
    task_id = Column(String(64), nullable=True, unique=True)
    analysis_id = Column(Integer, ForeignKey("analysis.id", ondelete="CASCADE"), nullable=False, unique=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    guest_session_id = Column(Integer, ForeignKey("guest_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    status = Column(String(24), nullable=False, default="pending", index=True)
    progress = Column(Integer, nullable=False, default=0)
    current_stage = Column(String(80), nullable=False, default="Validating video")
    original_filename = Column(String(255), nullable=False)
    stored_file_key = Column(String(500), nullable=False)
    duration_seconds = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    total_frames = Column(Integer, nullable=True)
    selected_frame_count = Column(Integer, nullable=False, default=0)
    processed_frame_count = Column(Integer, nullable=False, default=0)
    detected_track_count = Column(Integer, nullable=False, default=0)
    overall_result = Column(String(32), nullable=True)
    overall_confidence = Column(Float, nullable=True)
    primary_track_id = Column(Integer, nullable=True)
    error_code = Column(String(40), nullable=True)
    error_message_safe = Column(String(255), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)


class VideoFaceTrack(Base):
    __tablename__ = "video_face_tracks"

    id = Column(Integer, primary_key=True)
    video_job_id = Column(String(36), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    track_number = Column(Integer, nullable=False)
    first_timestamp_ms = Column(Integer, nullable=False)
    last_timestamp_ms = Column(Integer, nullable=False)
    frame_count = Column(Integer, nullable=False)
    median_fake_probability = Column(Float, nullable=False)
    maximum_fake_probability = Column(Float, nullable=False)
    suspicious_frame_count = Column(Integer, nullable=False)
    overall_result = Column(String(32), nullable=False)
    overall_confidence = Column(Float, nullable=False)
    quality_metadata = Column(JSON, nullable=True)


class VideoFrame(Base):
    __tablename__ = "video_frames"

    id = Column(Integer, primary_key=True)
    video_job_id = Column(String(36), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_ms = Column(Integer, nullable=False, index=True)
    frame_number = Column(Integer, nullable=False)
    track_id = Column(Integer, ForeignKey("video_face_tracks.id", ondelete="CASCADE"), nullable=True, index=True)
    face_index = Column(Integer, nullable=False, default=0)
    sampling_reason = Column(String(24), nullable=False)
    quality_score = Column(Float, nullable=False)
    prediction = Column(String(20), nullable=False)
    fake_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    thumbnail_key = Column(String(500), nullable=True)
    model_id = Column(String(120), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class VideoSegment(Base):
    __tablename__ = "video_segments"

    id = Column(Integer, primary_key=True)
    video_job_id = Column(String(36), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("video_face_tracks.id", ondelete="CASCADE"), nullable=True, index=True)
    start_timestamp_ms = Column(Integer, nullable=False)
    end_timestamp_ms = Column(Integer, nullable=False)
    result = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False)
    frame_count = Column(Integer, nullable=False)
    representative_thumbnail_key = Column(String(500), nullable=True)
