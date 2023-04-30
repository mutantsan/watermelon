"""Add water_facts table

Revision ID: ac25ec9cb5eb
Revises: 441e1bff8a23
Create Date: 2023-04-30 11:14:47.260660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ac25ec9cb5eb"
down_revision = "441e1bff8a23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "water_facts",
        sa.Column("id", sa.Text(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("used_facts", sa.LargeBinary(), nullable=True),
    )




def downgrade() -> None:
    op.drop_table("water_facts")
