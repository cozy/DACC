"""empty message

Revision ID: e9db87dd35b1
Revises: 985bc36a9cbc
Create Date: 2022-02-17 18:59:46.555511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e9db87dd35b1"
down_revision = "985bc36a9cbc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "aggregation",
        sa.Column("last_raw_measures_purged", sa.TIMESTAMP(), nullable=True),
    )
    op.add_column(
        "measure_definition",
        sa.Column(
            "max_days_to_update_quartile",
            sa.Integer(),
            server_default=sa.text("100"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("measure_definition", "max_days_to_update_quartile")
    op.drop_column("aggregation", "last_raw_measures_purged")
