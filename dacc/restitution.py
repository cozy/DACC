from dacc.models import Aggregation, tuple_as_dict
from dacc.utils import to_camel_case
from dacc.consts import AUTHORIZED_COLUMNS_FOR_RESTITUTION


def is_authorized_column(column_name):
    return column_name in AUTHORIZED_COLUMNS_FOR_RESTITUTION


def get_aggregated_results(params):
    """Get aggregated results for a measure.

    Note the number of contributions for a measure must be greater than
    the aggregation_threshold defined in the measure definition: otherwise,
    it won't be returned.

    Args:
        params (JSON): The JSON-formatted query parameters

    Returns:
        list(dict): A list of aggregates
    """
    measure_name = params.get("measureName")
    created_by = params.get("createdBy")
    start_date = params.get("startDate")
    end_date = params.get("endDate")

    aggs = Aggregation.query_range_with_threshold(
        measure_name, start_date, end_date, created_by
    )
    results = []
    for agg in aggs:
        # Use camelCase for JSON API
        columns_dict = tuple_as_dict(agg)
        res = {}
        for key in columns_dict.keys():
            if columns_dict[key] is not None and is_authorized_column(key):
                camel_key = to_camel_case(key)
                res[camel_key] = columns_dict[key]

        results.append(res)
    return results
