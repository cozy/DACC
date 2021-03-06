"""empty message

Revision ID: 5bafc336d30d
Revises: 5b38a673975a
Create Date: 2022-01-25 14:53:54.652526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5bafc336d30d"
down_revision = "5b38a673975a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "aggregation",
        sa.Column("median", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "aggregation",
        sa.Column(
            "first_quartile", sa.Numeric(precision=12, scale=2), nullable=True
        ),
    )
    op.add_column(
        "aggregation",
        sa.Column(
            "third_quartile", sa.Numeric(precision=12, scale=2), nullable=True
        ),
    )
    op.add_column(
        "measure_definition",
        sa.Column(
            "with_quartiles",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("measure_definition", "with_quartiles")
    op.drop_column("aggregation", "third_quartile")
    op.drop_column("aggregation", "first_quartile")
    op.drop_column("aggregation", "median")
    # ### end Alembic commands ###
