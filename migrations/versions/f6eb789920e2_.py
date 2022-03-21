"""empty message

Revision ID: f6eb789920e2
Revises: a161b799937a
Create Date: 2022-03-21 18:38:54.875430

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f6eb789920e2"
down_revision = "a161b799937a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "refused_raw_measure",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("measure_name", sa.String(length=100), nullable=True),
        sa.Column("value", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("start_date", sa.TIMESTAMP(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.Column("aggregation_period", sa.String(length=100), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column(
            "group1",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "group2",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "group3",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("rejected_date", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("refused_raw_measure")
