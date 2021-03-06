from dacc import consts
from datetime import datetime
from sqlalchemy.engine.reflection import Inspector
from alembic import op


def check_table_or_view_exists(name: str):
    """Check if a table or a view actually exists in database

    Args:
        name (str): The table or view name
    Returns:
        bool: True if the name matches an existing table or view.
    """
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


def to_camel_case(snake_str: str):
    """Convert a snake_case string to a camelCase

    Args:
        snake_str (str): the snake string

    Returns:
        str: the camel string
    """
    tokens = snake_str.split("_")
    return tokens[0] + "".join(x.title() for x in tokens[1:])
