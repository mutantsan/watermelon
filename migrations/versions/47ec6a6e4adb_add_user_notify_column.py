"""Add User.notify column

Revision ID: 47ec6a6e4adb
Revises:
Create Date: 2023-03-26 11:53:50.288969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "47ec6a6e4adb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("notify", sa.Boolean()))


def downgrade() -> None:
    op.drop_column("user", "notify")
