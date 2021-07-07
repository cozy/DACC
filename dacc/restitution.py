from dacc.models import Aggregation


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
        res = {}
        res["measureName"] = agg.measure_name
        res["startDate"] = agg.start_date
        res["createdBy"] = agg.created_by
        if agg.group1:
            res["group1"] = agg.group1
        if agg.group2:
            res["group2"] = agg.group2
        if agg.group3:
            res["group3"] = agg.group3
        res["sum"] = agg.sum
        res["count"] = agg.count
        res["countNotZero"] = agg.count_not_zero
        res["min"] = agg.min
        res["max"] = agg.max
        res["avg"] = agg.avg
        res["std"] = agg.std

        results.append(res)

    return results
