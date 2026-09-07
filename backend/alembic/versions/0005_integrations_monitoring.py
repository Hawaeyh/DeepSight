"""Add database-backed plans, usage reservations, payments, notifications and audit events.

Revision ID: 0005_integrations
Revises: 0004_media_detection
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_integrations"
down_revision = "0004_media_detection"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subscription_plans",
        sa.Column("code", sa.String(20), primary_key=True), sa.Column("name", sa.String(80), nullable=False),
        sa.Column("monthly_price", sa.Float(), nullable=False), sa.Column("annual_price", sa.Float(), nullable=False),
        sa.Column("image_limit", sa.Integer()), sa.Column("video_limit", sa.Integer()), sa.Column("webcam_limit", sa.Integer()), sa.Column("extension_limit", sa.Integer()),
        sa.Column("window_hours", sa.Integer()), sa.Column("history_retention_days", sa.Integer()),
        sa.Column("report_enabled", sa.Boolean(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("features", sa.JSON()),
    )
    plans = sa.table("subscription_plans", sa.column("code", sa.String), sa.column("name", sa.String), sa.column("monthly_price", sa.Float), sa.column("annual_price", sa.Float), sa.column("image_limit", sa.Integer), sa.column("video_limit", sa.Integer), sa.column("webcam_limit", sa.Integer), sa.column("extension_limit", sa.Integer), sa.column("window_hours", sa.Integer), sa.column("history_retention_days", sa.Integer), sa.column("report_enabled", sa.Boolean), sa.column("is_active", sa.Boolean), sa.column("features", sa.JSON))
    op.bulk_insert(plans, [
        {"code":"guest","name":"Guest","monthly_price":0,"annual_price":0,"image_limit":2,"video_limit":0,"webcam_limit":0,"extension_limit":0,"window_hours":24,"history_retention_days":1,"report_enabled":False,"is_active":True,"features":["2 image trials per day"]},
        {"code":"starter","name":"Starter","monthly_price":0,"annual_price":0,"image_limit":10,"video_limit":10,"webcam_limit":0,"extension_limit":0,"window_hours":12,"history_retention_days":90,"report_enabled":True,"is_active":True,"features":["Image and video detection","Personal history","Reports"]},
        {"code":"basic","name":"Basic","monthly_price":19,"annual_price":190,"image_limit":100,"video_limit":30,"webcam_limit":0,"extension_limit":100,"window_hours":12,"history_retention_days":365,"report_enabled":True,"is_active":True,"features":["Browser extension","Video analysis","Reports"]},
        {"code":"lite","name":"Lite","monthly_price":49,"annual_price":490,"image_limit":None,"video_limit":None,"webcam_limit":None,"extension_limit":None,"window_hours":None,"history_retention_days":None,"report_enabled":True,"is_active":True,"features":["Unlimited detection","Live webcam","Continuous extension"]},
    ])
    with op.batch_alter_table("account_entitlements") as batch:
        batch.add_column(sa.Column("user_id", sa.Integer(), nullable=True)); batch.add_column(sa.Column("stripe_customer_id", sa.String(120))); batch.add_column(sa.Column("stripe_subscription_id", sa.String(120))); batch.add_column(sa.Column("billing_interval", sa.String(20))); batch.add_column(sa.Column("current_period_end", sa.DateTime())); batch.add_column(sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.create_foreign_key("fk_account_entitlements_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE"); batch.create_unique_constraint("uq_account_entitlements_user_id", ["user_id"]); batch.create_unique_constraint("uq_account_entitlements_stripe_customer_id", ["stripe_customer_id"]); batch.create_unique_constraint("uq_account_entitlements_stripe_subscription_id", ["stripe_subscription_id"]); batch.create_index("ix_account_entitlements_user_id", ["user_id"])
    op.execute("UPDATE account_entitlements SET user_id = (SELECT users.id FROM users WHERE lower(users.email) = lower(account_entitlements.email))")
    with op.batch_alter_table("detection_usage") as batch:
        batch.add_column(sa.Column("reservation_key", sa.String(64))); batch.add_column(sa.Column("status", sa.String(20), nullable=False, server_default="completed")); batch.add_column(sa.Column("completed_at", sa.DateTime())); batch.add_column(sa.Column("released_at", sa.DateTime())); batch.create_unique_constraint("uq_detection_usage_reservation_key", ["reservation_key"]); batch.create_index("ix_detection_usage_reservation_key", ["reservation_key"]); batch.create_index("ix_detection_usage_status", ["status"])
    op.create_table("stripe_events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("event_id", sa.String(120), nullable=False), sa.Column("event_type", sa.String(100), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("customer_id", sa.String(120)), sa.Column("subscription_id", sa.String(120)), sa.Column("safe_metadata", sa.JSON()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.UniqueConstraint("event_id", name="uq_stripe_events_event_id"))
    op.create_index("ix_stripe_events_event_id", "stripe_events", ["event_id"]); op.create_index("ix_stripe_events_event_type", "stripe_events", ["event_type"])
    op.create_table("notifications", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("category", sa.String(40), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("message", sa.String(500), nullable=False), sa.Column("data", sa.JSON()), sa.Column("is_read", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"))
    for column in ("user_id","category","is_read","created_at"): op.create_index(f"ix_notifications_{column}", "notifications", [column])
    op.create_table("audit_events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("actor_user_id", sa.Integer()), sa.Column("action", sa.String(80), nullable=False), sa.Column("target_type", sa.String(50)), sa.Column("target_id", sa.String(80)), sa.Column("outcome", sa.String(20), nullable=False), sa.Column("details", sa.JSON()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"))
    for column in ("actor_user_id","action","created_at"): op.create_index(f"ix_audit_events_{column}", "audit_events", [column])
    op.create_table("webcam_sessions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("owner_user_id", sa.Integer(), nullable=False), sa.Column("usage_reservation_key", sa.String(64)), sa.Column("status", sa.String(20), nullable=False), sa.Column("valid_frame_count", sa.Integer(), nullable=False), sa.Column("predictions", sa.JSON()), sa.Column("final_result", sa.String(32)), sa.Column("final_confidence", sa.Float()), sa.Column("analysis_id", sa.Integer()), sa.Column("started_at", sa.DateTime(), nullable=False), sa.Column("ended_at", sa.DateTime()), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["analysis_id"], ["analysis.id"], ondelete="SET NULL"))
    op.create_index("ix_webcam_sessions_owner_user_id", "webcam_sessions", ["owner_user_id"]); op.create_index("ix_webcam_sessions_status", "webcam_sessions", ["status"])


def downgrade():
    op.drop_index("ix_webcam_sessions_status", table_name="webcam_sessions"); op.drop_index("ix_webcam_sessions_owner_user_id", table_name="webcam_sessions"); op.drop_table("webcam_sessions")
    for table, columns in (("audit_events",("created_at","action","actor_user_id")),("notifications",("created_at","is_read","category","user_id"))):
        for column in columns: op.drop_index(f"ix_{table}_{column}", table_name=table)
        op.drop_table(table)
    op.drop_index("ix_stripe_events_event_type", table_name="stripe_events"); op.drop_index("ix_stripe_events_event_id", table_name="stripe_events"); op.drop_table("stripe_events")
    with op.batch_alter_table("detection_usage") as batch:
        batch.drop_index("ix_detection_usage_status"); batch.drop_index("ix_detection_usage_reservation_key"); batch.drop_constraint("uq_detection_usage_reservation_key", type_="unique"); batch.drop_column("released_at"); batch.drop_column("completed_at"); batch.drop_column("status"); batch.drop_column("reservation_key")
    with op.batch_alter_table("account_entitlements") as batch:
        batch.drop_index("ix_account_entitlements_user_id"); batch.drop_constraint("uq_account_entitlements_stripe_subscription_id", type_="unique"); batch.drop_constraint("uq_account_entitlements_stripe_customer_id", type_="unique"); batch.drop_constraint("uq_account_entitlements_user_id", type_="unique"); batch.drop_constraint("fk_account_entitlements_user_id_users", type_="foreignkey"); batch.drop_column("cancel_at_period_end"); batch.drop_column("current_period_end"); batch.drop_column("billing_interval"); batch.drop_column("stripe_subscription_id"); batch.drop_column("stripe_customer_id"); batch.drop_column("user_id")
    op.drop_table("subscription_plans")
