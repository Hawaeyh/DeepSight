"""Create the schema matching the pre-Alembic DeepSight SQLite models.

Revision ID: 0001_initial_schema
Revises: None
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_extension", sa.String(length=10), nullable=True),
        sa.Column("file_size", sa.Float(), nullable=True),
        sa.Column("prediction", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("real_probability", sa.Float(), nullable=True),
        sa.Column("fake_probability", sa.Float(), nullable=True),
        sa.Column("deepfake_type", sa.String(length=100), nullable=True),
        sa.Column("type_confidence", sa.Float(), nullable=True),
        sa.Column("face_detected", sa.Boolean(), nullable=True),
        sa.Column("face_count", sa.Integer(), nullable=True),
        sa.Column("image_width", sa.Integer(), nullable=True),
        sa.Column("image_height", sa.Integer(), nullable=True),
        sa.Column("video_duration", sa.Float(), nullable=True),
        sa.Column("frames_analyzed", sa.Integer(), nullable=True),
        sa.Column("fake_frames", sa.Integer(), nullable=True),
        sa.Column("real_frames", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("device", sa.String(length=20), nullable=False),
        sa.Column("processing_time", sa.Float(), nullable=False),
        sa.Column("verified_result", sa.String(length=20), nullable=True),
        sa.Column("remarks", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_analysis")),
    )
    op.create_index(op.f("ix_analysis_id"), "analysis", ["id"], unique=False)

    op.create_table(
        "account_entitlements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account_entitlements")),
    )
    op.create_index(
        op.f("ix_account_entitlements_email"),
        "account_entitlements",
        ["email"],
        unique=True,
    )
    op.create_index(
        op.f("ix_account_entitlements_id"),
        "account_entitlements",
        ["id"],
        unique=False,
    )

    op.create_table(
        "detection_usage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identity", sa.String(length=255), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_detection_usage")),
    )
    op.create_index(
        op.f("ix_detection_usage_created_at"),
        "detection_usage",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_detection_usage_identity"),
        "detection_usage",
        ["identity"],
        unique=False,
    )
    op.create_index(
        op.f("ix_detection_usage_id"),
        "detection_usage",
        ["id"],
        unique=False,
    )

    op.create_table(
        "analysis_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("corrected_prediction", sa.String(length=20), nullable=True),
        sa.Column("fake_category", sa.String(length=40), nullable=True),
        sa.Column("manipulation_type", sa.String(length=100), nullable=True),
        sa.Column("original_file_path", sa.String(length=500), nullable=True),
        sa.Column("hard_example_path", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_analysis_feedback")),
    )
    op.create_index(
        op.f("ix_analysis_feedback_analysis_id"),
        "analysis_feedback",
        ["analysis_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analysis_feedback_id"),
        "analysis_feedback",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_analysis_feedback_id"), table_name="analysis_feedback")
    op.drop_index(op.f("ix_analysis_feedback_analysis_id"), table_name="analysis_feedback")
    op.drop_table("analysis_feedback")
    op.drop_index(op.f("ix_detection_usage_id"), table_name="detection_usage")
    op.drop_index(op.f("ix_detection_usage_identity"), table_name="detection_usage")
    op.drop_index(op.f("ix_detection_usage_created_at"), table_name="detection_usage")
    op.drop_table("detection_usage")
    op.drop_index(op.f("ix_account_entitlements_id"), table_name="account_entitlements")
    op.drop_index(op.f("ix_account_entitlements_email"), table_name="account_entitlements")
    op.drop_table("account_entitlements")
    op.drop_index(op.f("ix_analysis_id"), table_name="analysis")
    op.drop_table("analysis")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
