"""empty message

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
    # op.drop_table('measures_definition')
    # op.drop_table('raw_measures')
    # op.drop_table('aggregation_dates')
    print("First version - nothing to do")


def downgrade():
    op.create_table(
        "aggregation_dates",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "measures_definition_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "last_aggregated_measure_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["measures_definition_id"],
            ["measures_definition.id"],
            name="aggregation_dates_measures_definition_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="aggregation_dates_pkey"),
    )
    op.create_table(
        "raw_measures",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "measure_name",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "value",
            sa.NUMERIC(precision=12, scale=2),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "start_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "last_updated",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "aggregation_period",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_by",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "group1",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "group2",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "group3",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "is_aggregated", sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name="raw_measures_pkey"),
    )
    op.create_table(
        "measures_definition",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "name", sa.VARCHAR(length=100), autoincrement=False, nullable=True
        ),
        sa.Column(
            "org", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
        sa.Column(
            "created_by",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "group1_key",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "group2_key",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "group3_key",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "description", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "aggregation_period",
            sa.VARCHAR(length=50),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "contribution_threshold",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name="measures_definition_pkey"),
        sa.UniqueConstraint("name", name="measures_definition_name_key"),
    )
