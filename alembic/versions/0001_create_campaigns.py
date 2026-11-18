"""create campaigns table

Revision ID: 0001
Revises:
Create Date: 2026-11-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("keitaro_id", sa.Integer(), nullable=True),
        sa.Column("alias", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("geo", sa.JSON(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campaigns")),
        sa.UniqueConstraint("keitaro_id", name=op.f("uq_campaigns_keitaro_id")),
        sa.UniqueConstraint("alias", name=op.f("uq_campaigns_alias")),
        sa.UniqueConstraint("name", name=op.f("uq_campaigns_name")),
    )
    op.create_index(op.f("ix_campaigns_status"), "campaigns", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_campaigns_status"), table_name="campaigns")
    op.drop_table("campaigns")
