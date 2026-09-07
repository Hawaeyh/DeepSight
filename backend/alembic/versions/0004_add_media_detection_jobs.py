"""Add image quality metadata and asynchronous video job tables.

Revision ID: 0004_media_detection
Revises: 0003_security_ownership
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_media_detection"
down_revision: Union[str, None] = "0003_security_ownership"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("analysis") as batch:
        batch.add_column(sa.Column("quality_metadata", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("quality_warnings", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("selected_face_index", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("selected_face_box", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("face_detection_confidence", sa.Float(), nullable=True))
    op.create_table(
        "video_jobs",
        sa.Column("id", sa.String(36), nullable=False), sa.Column("task_id", sa.String(64), nullable=True),
        sa.Column("analysis_id", sa.Integer(), nullable=False), sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("guest_session_id", sa.Integer(), nullable=True), sa.Column("status", sa.String(24), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False), sa.Column("current_stage", sa.String(80), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False), sa.Column("stored_file_key", sa.String(500), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True), sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True), sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("total_frames", sa.Integer(), nullable=True), sa.Column("selected_frame_count", sa.Integer(), nullable=False),
        sa.Column("processed_frame_count", sa.Integer(), nullable=False), sa.Column("detected_track_count", sa.Integer(), nullable=False),
        sa.Column("overall_result", sa.String(32), nullable=True), sa.Column("overall_confidence", sa.Float(), nullable=True),
        sa.Column("primary_track_id", sa.Integer(), nullable=True), sa.Column("error_code", sa.String(40), nullable=True),
        sa.Column("error_message_safe", sa.String(255), nullable=True), sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True), sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis.id"], name=op.f("fk_video_jobs_analysis_id_analysis"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], name=op.f("fk_video_jobs_owner_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["guest_session_id"], ["guest_sessions.id"], name=op.f("fk_video_jobs_guest_session_id_guest_sessions"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_video_jobs")), sa.UniqueConstraint("analysis_id", name=op.f("uq_video_jobs_analysis_id")),
        sa.UniqueConstraint("task_id", name=op.f("uq_video_jobs_task_id")),
    )
    for column in ("analysis_id", "owner_user_id", "guest_session_id", "status", "created_at"):
        op.create_index(op.f(f"ix_video_jobs_{column}"), "video_jobs", [column])
    op.create_table(
        "video_face_tracks", sa.Column("id", sa.Integer(), nullable=False), sa.Column("video_job_id", sa.String(36), nullable=False),
        sa.Column("track_number", sa.Integer(), nullable=False), sa.Column("first_timestamp_ms", sa.Integer(), nullable=False),
        sa.Column("last_timestamp_ms", sa.Integer(), nullable=False), sa.Column("frame_count", sa.Integer(), nullable=False),
        sa.Column("median_fake_probability", sa.Float(), nullable=False), sa.Column("maximum_fake_probability", sa.Float(), nullable=False),
        sa.Column("suspicious_frame_count", sa.Integer(), nullable=False), sa.Column("overall_result", sa.String(32), nullable=False),
        sa.Column("overall_confidence", sa.Float(), nullable=False), sa.Column("quality_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["video_job_id"], ["video_jobs.id"], name=op.f("fk_video_face_tracks_video_job_id_video_jobs"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_video_face_tracks")),
    )
    op.create_index(op.f("ix_video_face_tracks_video_job_id"), "video_face_tracks", ["video_job_id"])
    op.create_table(
        "video_frames", sa.Column("id", sa.Integer(), nullable=False), sa.Column("video_job_id", sa.String(36), nullable=False),
        sa.Column("timestamp_ms", sa.Integer(), nullable=False), sa.Column("frame_number", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=True), sa.Column("face_index", sa.Integer(), nullable=False),
        sa.Column("sampling_reason", sa.String(24), nullable=False), sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("prediction", sa.String(20), nullable=False), sa.Column("fake_probability", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False), sa.Column("thumbnail_key", sa.String(500), nullable=True),
        sa.Column("model_id", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["video_job_id"], ["video_jobs.id"], name=op.f("fk_video_frames_video_job_id_video_jobs"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["track_id"], ["video_face_tracks.id"], name=op.f("fk_video_frames_track_id_video_face_tracks"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_video_frames")),
    )
    for column in ("video_job_id", "timestamp_ms", "track_id"):
        op.create_index(op.f(f"ix_video_frames_{column}"), "video_frames", [column])
    op.create_table(
        "video_segments", sa.Column("id", sa.Integer(), nullable=False), sa.Column("video_job_id", sa.String(36), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=True), sa.Column("start_timestamp_ms", sa.Integer(), nullable=False),
        sa.Column("end_timestamp_ms", sa.Integer(), nullable=False), sa.Column("result", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False), sa.Column("frame_count", sa.Integer(), nullable=False),
        sa.Column("representative_thumbnail_key", sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(["video_job_id"], ["video_jobs.id"], name=op.f("fk_video_segments_video_job_id_video_jobs"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["track_id"], ["video_face_tracks.id"], name=op.f("fk_video_segments_track_id_video_face_tracks"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_video_segments")),
    )
    for column in ("video_job_id", "track_id"):
        op.create_index(op.f(f"ix_video_segments_{column}"), "video_segments", [column])


def downgrade() -> None:
    for table, columns in (("video_segments", ("track_id", "video_job_id")), ("video_frames", ("track_id", "timestamp_ms", "video_job_id")), ("video_face_tracks", ("video_job_id",))):
        for column in columns: op.drop_index(op.f(f"ix_{table}_{column}"), table_name=table)
        op.drop_table(table)
    for column in ("created_at", "status", "guest_session_id", "owner_user_id", "analysis_id"):
        op.drop_index(op.f(f"ix_video_jobs_{column}"), table_name="video_jobs")
    op.drop_table("video_jobs")
    with op.batch_alter_table("analysis") as batch:
        for column in ("face_detection_confidence", "selected_face_box", "selected_face_index", "quality_warnings", "quality_metadata"):
            batch.drop_column(column)
