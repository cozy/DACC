"""Initial schema

Revision ID: 0670ff313bf0
Revises:
Create Date: 2021-06-14 11:53:08.583479

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0670ff313bf0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "aggregation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("measure_name", sa.String(length=100), nullable=True),
        sa.Column("start_date", sa.TIMESTAMP(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
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
        sa.Column("sum", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.Column("count_not_zero", sa.Integer(), nullable=True),
        sa.Column("min", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("max", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("avg", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("std", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "measure_definition",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("org", sa.String(length=50), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("group1_key", sa.String(length=100), nullable=True),
        sa.Column("group2_key", sa.String(length=100), nullable=True),
        sa.Column("group3_key", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("aggregation_period", sa.String(length=50), nullable=True),
        sa.Column("execution_frequency", sa.String(length=50), nullable=True),
        sa.Column(
            "aggregation_threshold",
            sa.Integer(),
            server_default=sa.text("5"),
            nullable=True,
        ),
        sa.Column("access_app", sa.Boolean(), nullable=True),
        sa.Column("access_public", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "raw_measure",
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "aggregation_date",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("measure_definition_id", sa.Integer(), nullable=True),
        sa.Column(
            "last_aggregated_measure_date", sa.TIMESTAMP(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["measure_definition_id"],
            ["measure_definition.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("aggregation_date")
    op.drop_table("raw_measure")
    op.drop_table("measure_definition")
    op.drop_table("aggregation")
