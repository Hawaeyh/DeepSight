"""Add audited feedback integrity and current analysis query indexes.

Revision ID: 0002_integrity_indexes
Revises: 0001_initial_schema
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0002_integrity_indexes"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f("ix_analysis_created_at"), "analysis", ["created_at"], unique=False)
    op.create_index(op.f("ix_analysis_file_type"), "analysis", ["file_type"], unique=False)
    op.create_index(op.f("ix_analysis_model_name"), "analysis", ["model_name"], unique=False)
    op.create_index(op.f("ix_analysis_prediction"), "analysis", ["prediction"], unique=False)
    with op.batch_alter_table("analysis_feedback") as batch_op:
        batch_op.create_foreign_key(
            op.f("fk_analysis_feedback_analysis_id_analysis"),
            "analysis",
            ["analysis_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("analysis_feedback") as batch_op:
        batch_op.drop_constraint(
            op.f("fk_analysis_feedback_analysis_id_analysis"),
            type_="foreignkey",
        )
    op.drop_index(op.f("ix_analysis_prediction"), table_name="analysis")
    op.drop_index(op.f("ix_analysis_model_name"), table_name="analysis")
    op.drop_index(op.f("ix_analysis_file_type"), table_name="analysis")
    op.drop_index(op.f("ix_analysis_created_at"), table_name="analysis")
