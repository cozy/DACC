import pytest
from dacc import db, aggregation
from dacc.models import RawMeasures, AggregationDates, Aggregation
import pandas as pd
from sqlalchemy import distinct
from datetime import datetime


def query_all_measures_name():
    results = db.session.query(distinct(RawMeasures.measure_name)).all()
    return [v for v, in results]


def convert_columns(df_raw):
    if "group1" in df_raw:
        df_raw = df_raw.astype({"group1": "str"})
    if "group2" in df_raw:
        df_raw = df_raw.astype({"group2": "str"})
    if "group3" in df_raw:
        df_raw = df_raw.astype({"group3": "str"})
    df_raw = df_raw.astype({"value": "float"})
    return df_raw


def test_aggregations():
    measure_names = query_all_measures_name()
    for measure_name in measure_names:
        aggregated_rows = aggregation.query_measures_to_aggregate_by_name(
            measure_name, None, None
        )

        raw_measures = RawMeasures.query_by_name(measure_name)

        df_raw = pd.DataFrame(
            data=raw_measures,
            columns=[
                "created_by",
                "start_date",
                "group1",
                "group2",
                "group3",
                "value",
            ],
        )

        #  Remove null columns
        columns = df_raw.columns[df_raw.notna().any()].tolist()
        df_raw = df_raw.dropna(axis="columns")

        df_raw = convert_columns(df_raw)
        columns.remove("value")  #  Remove value column to group by

        sums = df_raw.groupby(columns, as_index=False).sum()
        counts = df_raw.groupby(columns, as_index=False).count()
        mins = df_raw.groupby(columns, as_index=False).min()
        maxs = df_raw.groupby(columns, as_index=False).max()
        avgs = df_raw.groupby(columns, as_index=False).mean()

        assert len(aggregated_rows) == len(sums)
        for i, _ in enumerate(aggregated_rows):
            assert aggregated_rows[i].sum == sums.value[i]
            assert aggregated_rows[i].count == counts.value[i]
            assert aggregated_rows[i].min == mins.value[i]
            assert aggregated_rows[i].max == maxs.value[i]
            assert aggregated_rows[i].avg == avgs.value[i]


def test_time_interval():
    # The indicator does not exist
    start_date, end_date = aggregation.find_time_interval("wrong-measure")
    assert start_date is None
    assert end_date is None

    # No raw measure for this indicator
    start_date, end_date = aggregation.find_time_interval(
        "energy-consumption-daily"
    )
    assert start_date is None
    assert end_date is None

    # Raw measures exist but no aggregation date
    start_date, end_date = aggregation.find_time_interval(
        "connection-count-daily"
    )
    assert start_date == datetime.min
    assert end_date == datetime(2021, 5, 3, 0, 0, 0, 4000)

    # Raw measures exist with aggregation date
    m_date = datetime(2021, 5, 1, 0, 0, 0, 0)
    agg_date = AggregationDates(
        measures_definition_id=1,
        last_aggregated_measure_date=m_date,
    )
    db.session.add(agg_date)
    start_date, end_date = aggregation.find_time_interval(
        "connection-count-daily"
    )
    assert start_date == m_date
    assert end_date == datetime(2021, 5, 3, 0, 0, 0, 4000)

    db.session.rollback()


def test_new_aggregation_date():
    agg_date = aggregation.get_new_aggregation_date("wrong-measure", None)
    assert agg_date is None

    date = datetime(2021, 5, 1, 0, 0, 0, 0)
    agg_date = aggregation.get_new_aggregation_date(
        "connection-count-daily", date
    )
    assert agg_date.measures_definition_id == 1
    assert agg_date.last_aggregated_measure_date == date

    db.session.add(agg_date)
    date = datetime(2021, 5, 2, 0, 0, 0, 0)
    agg_date = aggregation.get_new_aggregation_date(
        "connection-count-daily", date
    )
    assert agg_date.measures_definition_id == 1
    assert agg_date.last_aggregated_measure_date == date


def test_compute_partial_aggregates():
    curr_agg = Aggregation(measure_name="dummy1")
    new_agg = Aggregation(measure_name="dummy2")
    with pytest.raises(Exception) as e_info:
        aggregation.compute_partial_aggregates("dummy2", curr_agg, new_agg)
    assert "Cannot compute aggregation on different measures" in str(
        e_info.value
    )

    curr_agg = Aggregation(measure_name="dummy1", start_date="2020-05-01")
    new_agg = Aggregation(measure_name="dummy1", start_date="2020-05-02")
    with pytest.raises(Exception) as e_info:
        aggregation.compute_partial_aggregates("dummy1", curr_agg, new_agg)
    assert "Cannot compute aggregation on different dates" in str(e_info.value)

    measure_name = "connection-count-daily"
    start_date = "2021-05-01"
    curr_agg = Aggregation(
        measure_name=measure_name,
        start_date=start_date,
        sum=40,
        count=4,
        min=5,
        max=15,
        avg=10,
    )
    new_agg = Aggregation(
        measure_name=measure_name,
        start_date=start_date,
        sum=26,
        count=2,
        min=6,
        max=20,
        avg=13,
    )
    agg = aggregation.compute_partial_aggregates(
        measure_name, curr_agg, new_agg
    )
    assert agg.count == 6
    assert agg.sum == 66
    assert agg.min == 5
    assert agg.max == 20
    assert agg.avg == 11
