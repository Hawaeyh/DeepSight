"""Add Firebase identity metadata and database-owned Stripe price mapping.

Revision ID: 0006_external_identity_billing
Revises: 0005_integrations
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_external_identity_billing"
down_revision = "0005_integrations"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("analysis") as batch:
        batch.alter_column("source", existing_type=sa.String(20), type_=sa.String(40), existing_nullable=True)
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("firebase_email", sa.String(255), nullable=True))
        batch.add_column(sa.Column("firebase_provider", sa.String(40), nullable=True))
        batch.add_column(sa.Column("firebase_linked_at", sa.DateTime(), nullable=True))
    with op.batch_alter_table("subscription_plans") as batch:
        batch.add_column(sa.Column("stripe_monthly_price_id", sa.String(120), nullable=True))
        batch.add_column(sa.Column("stripe_annual_price_id", sa.String(120), nullable=True))
        batch.create_unique_constraint("uq_subscription_plans_stripe_monthly_price_id", ["stripe_monthly_price_id"])
        batch.create_unique_constraint("uq_subscription_plans_stripe_annual_price_id", ["stripe_annual_price_id"])
    with op.batch_alter_table("account_entitlements") as batch:
        batch.add_column(sa.Column("stripe_price_id", sa.String(120), nullable=True))
        batch.add_column(sa.Column("current_period_start", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("provider", sa.String(20), nullable=False, server_default="local"))
    op.create_table(
        "extension_video_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("usage_reservation_key", sa.String(64), nullable=True),
        sa.Column("selected_model_id", sa.String(80), nullable=False),
        sa.Column("actual_model_id", sa.String(80), nullable=True),
        sa.Column("page_domain", sa.String(253), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("frames_received", sa.Integer(), nullable=False),
        sa.Column("frames_analysed", sa.Integer(), nullable=False),
        sa.Column("frames_skipped", sa.Integer(), nullable=False),
        sa.Column("suspicious_frames", sa.Integer(), nullable=False),
        sa.Column("predictions", sa.JSON(), nullable=True),
        sa.Column("overall_result", sa.String(32), nullable=True),
        sa.Column("overall_confidence", sa.Float(), nullable=True),
        sa.Column("failure_code", sa.String(40), nullable=True),
        sa.Column("analysis_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["analysis_id"], ["analysis.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_extension_video_sessions_owner_user_id", "extension_video_sessions", ["owner_user_id"])
    op.create_index("ix_extension_video_sessions_status", "extension_video_sessions", ["status"])


def downgrade():
    op.drop_index("ix_extension_video_sessions_status", table_name="extension_video_sessions")
    op.drop_index("ix_extension_video_sessions_owner_user_id", table_name="extension_video_sessions")
    op.drop_table("extension_video_sessions")
    with op.batch_alter_table("analysis") as batch:
        batch.alter_column("source", existing_type=sa.String(40), type_=sa.String(20), existing_nullable=True)
    with op.batch_alter_table("account_entitlements") as batch:
        batch.drop_column("provider")
        batch.drop_column("current_period_start")
        batch.drop_column("stripe_price_id")
    with op.batch_alter_table("subscription_plans") as batch:
        batch.drop_constraint("uq_subscription_plans_stripe_annual_price_id", type_="unique")
        batch.drop_constraint("uq_subscription_plans_stripe_monthly_price_id", type_="unique")
        batch.drop_column("stripe_annual_price_id")
        batch.drop_column("stripe_monthly_price_id")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("firebase_linked_at")
        batch.drop_column("firebase_provider")
        batch.drop_column("firebase_email")
