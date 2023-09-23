"""add drink_type table

Revision ID: c0b2a0653f1c
Revises: ac25ec9cb5eb
Create Date: 2023-09-23 08:59:01.813060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0b2a0653f1c'
down_revision = 'ac25ec9cb5eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "drink_type",
        sa.Column("id", sa.Text(length=36), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("coefficient", sa.Integer(), nullable=False),
    )




def downgrade() -> None:
    op.drop_table("drink_type")
