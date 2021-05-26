from dacc import dacc, db, aggregation
from dacc.models import RawMeasures

def test_aggregation():
    measure_name = 'connection-count-daily'
    aggregated_rows = aggregation.query_measures_to_aggregate_by_name(measure_name)

    assert aggregated_rows.count() == 3
    assert aggregated_rows[0].sum == 15
    assert aggregated_rows[1].sum == 8
    assert aggregated_rows[2].sum == 6