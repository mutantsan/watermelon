"""Add notification_settings table

Revision ID: 441e1bff8a23
Revises: f2cf9b8f3ec2
Create Date: 2023-04-22 17:30:33.723004

"""
from uuid import uuid4
from datetime import datetime as dt

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "441e1bff8a23"
down_revision = "f2cf9b8f3ec2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_settings",
        sa.Column(
            "id",
            sa.Text(length=36),
            nullable=False,
            default=lambda: str(uuid4()),
        ),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("user.id"), primary_key=True
        ),
        sa.Column("start_time", sa.Integer(), nullable=False, default="8"),
        sa.Column("end_time", sa.Integer(), nullable=False, default="22"),
        sa.Column("frequency", sa.Integer(), nullable=False, default="15"),
        sa.Column(
            "notified_at", sa.DateTime(), nullable=True, default=dt.utcnow
        ),
    )


def downgrade() -> None:
    op.drop_table("notification_settings")
