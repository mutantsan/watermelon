"""Add user.timezone column

Revision ID: edaf14fc9828
Revises: 47ec6a6e4adb
Create Date: 2023-04-02 15:52:32.002435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "edaf14fc9828"
down_revision = "47ec6a6e4adb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("timezone", sa.String(), server_default="Europe/Kiev"),
    )


def downgrade() -> None:
    op.drop_column("user", "timezone")
