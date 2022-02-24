"""empty message

Revision ID: a161b799937a
Revises: e9db87dd35b1
Create Date: 2022-02-24 13:26:56.553441

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a161b799937a"
down_revision = "e9db87dd35b1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "idx_by_mname_and_sdate",
        "aggregation",
        ["measure_name", "start_date"],
        unique=False,
    )
    op.create_index(
        "idx_by_mname_and_sdate_and_created_by_and_groups",
        "aggregation",
        [
            "measure_name",
            "start_date",
            "created_by",
            "group1",
            "group2",
            "group3",
        ],
        unique=False,
    )
    op.create_index(
        "idx_by_mname_and_lupdated",
        "raw_measure",
        ["measure_name", "last_updated"],
        unique=False,
    )


def downgrade():
    op.drop_index("idx_by_mname_and_lupdated", table_name="raw_measure")
    op.drop_index(
        "idx_by_mname_and_sdate_and_created_by_and_groups",
        table_name="aggregation",
    )
    op.drop_index("idx_by_mname_and_sdate", table_name="aggregation")
