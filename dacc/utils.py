from dacc import consts
from datetime import datetime


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
