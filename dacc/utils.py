from dacc import consts
from datetime import datetime
from sqlalchemy.engine.reflection import Inspector
from alembic import op


def check_table_or_view_exists(name):
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    views = inspector.get_view_names()
    objects = tables + views
    return name in objects


def is_dates_interval_higher(
    start_date: datetime, end_date: datetime, period: str
):
    """Check if the date interval is higher than the given period

    Args:
        start_date (datetime): The starting date
        end_date (datetime): The ending date
        period (str): The time period (day, week, month)

    Returns:
        bool: True is the date interval is higher
    """

    if period is None:
        period = consts.DAY_PERIOD

    diff = (end_date - start_date).days / consts.TIME_PERIOD[period]
    return diff >= 1
