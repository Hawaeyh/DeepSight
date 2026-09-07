"""Add trusted identity metadata, analysis ownership, and guest sessions.

Revision ID: 0003_security_ownership
Revises: 0002_integrity_indexes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_security_ownership"
down_revision: Union[str, None] = "0002_integrity_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("firebase_uid", sa.String(length=128), nullable=True))
        batch_op.add_column(
            sa.Column(
                "authentication_source",
                sa.String(length=20),
                server_default="local",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column("email_verified", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
        batch_op.create_index(op.f("ix_users_firebase_uid"), ["firebase_uid"], unique=True)

    op.create_table(
        "guest_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("user_agent_hash", sa.String(length=64), nullable=True),
        sa.Column("analysis_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("transferred_at", sa.DateTime(), nullable=True),
        sa.Column("transferred_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["transferred_user_id"], ["users.id"], name=op.f("fk_guest_sessions_transferred_user_id_users"), ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guest_sessions")),
    )
    op.create_index(op.f("ix_guest_sessions_id"), "guest_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_guest_sessions_token_hash"), "guest_sessions", ["token_hash"], unique=True)
    op.create_index(op.f("ix_guest_sessions_expires_at"), "guest_sessions", ["expires_at"], unique=False)

    with op.batch_alter_table("analysis") as batch_op:
        batch_op.add_column(sa.Column("owner_user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("guest_session_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("source", sa.String(length=20), nullable=True))
        batch_op.create_foreign_key(
            op.f("fk_analysis_owner_user_id_users"), "users", ["owner_user_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_foreign_key(
            op.f("fk_analysis_guest_session_id_guest_sessions"),
            "guest_sessions", ["guest_session_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_check_constraint(
            op.f("ck_analysis_analysis_single_owner"),
            "NOT (owner_user_id IS NOT NULL AND guest_session_id IS NOT NULL)",
        )
        batch_op.create_index(op.f("ix_analysis_owner_user_id"), ["owner_user_id"], unique=False)
        batch_op.create_index(op.f("ix_analysis_guest_session_id"), ["guest_session_id"], unique=False)
        batch_op.create_index(op.f("ix_analysis_source"), ["source"], unique=False)
        batch_op.create_index(
            "ix_analysis_owner_user_id_created_at", ["owner_user_id", "created_at"], unique=False
        )

    with op.batch_alter_table("analysis_feedback") as batch_op:
        batch_op.add_column(sa.Column("owner_user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            op.f("fk_analysis_feedback_owner_user_id_users"),
            "users", ["owner_user_id"], ["id"], ondelete="SET NULL"
        )
        batch_op.create_index(op.f("ix_analysis_feedback_owner_user_id"), ["owner_user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("analysis_feedback") as batch_op:
        batch_op.drop_index(op.f("ix_analysis_feedback_owner_user_id"))
        batch_op.drop_constraint(op.f("fk_analysis_feedback_owner_user_id_users"), type_="foreignkey")
        batch_op.drop_column("owner_user_id")
    with op.batch_alter_table("analysis") as batch_op:
        batch_op.drop_index("ix_analysis_owner_user_id_created_at")
        batch_op.drop_index(op.f("ix_analysis_guest_session_id"))
        batch_op.drop_index(op.f("ix_analysis_source"))
        batch_op.drop_index(op.f("ix_analysis_owner_user_id"))
        batch_op.drop_constraint(op.f("ck_analysis_analysis_single_owner"), type_="check")
        batch_op.drop_constraint(op.f("fk_analysis_guest_session_id_guest_sessions"), type_="foreignkey")
        batch_op.drop_constraint(op.f("fk_analysis_owner_user_id_users"), type_="foreignkey")
        batch_op.drop_column("guest_session_id")
        batch_op.drop_column("source")
        batch_op.drop_column("owner_user_id")
    op.drop_index(op.f("ix_guest_sessions_expires_at"), table_name="guest_sessions")
    op.drop_index(op.f("ix_guest_sessions_token_hash"), table_name="guest_sessions")
    op.drop_index(op.f("ix_guest_sessions_id"), table_name="guest_sessions")
    op.drop_table("guest_sessions")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index(op.f("ix_users_firebase_uid"))
        batch_op.drop_column("email_verified")
        batch_op.drop_column("authentication_source")
        batch_op.drop_column("firebase_uid")
