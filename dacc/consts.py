import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

DAY_PERIOD = "day"
WEEK_PERIOD = "week"
MONTH_PERIOD = "month"

TIME_PERIOD = {DAY_PERIOD: 1, WEEK_PERIOD: 7, MONTH_PERIOD: 30}

AUTHORIZED_COLUMNS_FOR_RESTITUTION = [
    "measure_name",
    "start_date",
    "created_by",
    "group1",
    "group2",
    "group3",
    "sum",
    "count",
    "count_not_zero",
    "min",
    "max",
    "avg",
    "std",
    "median",
    "first_quartile",
    "third_quartile",
]
