"""empty message

Revision ID: 5b38a673975a
Revises: 0670ff313bf0
Create Date: 2021-06-14 14:56:24.645790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b38a673975a"
down_revision = "0670ff313bf0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("org", sa.String(length=100), nullable=True),
        sa.Column("token", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("auth")
