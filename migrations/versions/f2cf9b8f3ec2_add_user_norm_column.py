"""Add user.norm column

Revision ID: f2cf9b8f3ec2
Revises: edaf14fc9828
Create Date: 2023-04-16 09:22:09.610639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2cf9b8f3ec2"
down_revision = "edaf14fc9828"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("norm", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "norm")
