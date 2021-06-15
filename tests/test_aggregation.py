import pytest
from dacc import db, aggregation
from dacc.models import (
    RawMeasure,
    AggregationDate,
    Aggregation,
    MeasureDefinition,
)
import pandas as pd
from sqlalchemy import distinct
import numpy as np
from datetime import datetime, timedelta


def query_all_measures_name():
    results = db.session.query(distinct(RawMeasure.measure_name)).all()
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
        aggregated_rows = aggregation.aggregate_measures_from_db(
            measure_name, None, None
        )

        raw_measures = RawMeasure.query_by_name(measure_name)

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
        stds = df_raw.groupby(columns, as_index=False).std()
        stds = stds.fillna(0)

        assert len(aggregated_rows) == len(sums)
        for i, _ in enumerate(aggregated_rows):
            assert aggregated_rows[i].sum == sums.value[i]
            assert aggregated_rows[i].count == counts.value[i]
            assert aggregated_rows[i].min == mins.value[i]
            assert aggregated_rows[i].max == maxs.value[i]
            assert round(float(aggregated_rows[i].avg), 4) == round(
                avgs.value[i], 4
            )
            assert round(float(aggregated_rows[i].std), 2) == round(
                stds.value[i], 2
            )


def test_aggregate_dates():
    measure_name = "dummy"
    measures = [
        RawMeasure(
            measure_name=measure_name,
            start_date="2021-05-01",
            last_updated="2021-05-01T00:00:01",
            value=42,
        ),
        RawMeasure(
            measure_name=measure_name,
            start_date="2021-05-01",
            last_updated="2021-05-02",
            value=42,
        ),
        RawMeasure(
            measure_name=measure_name,
            start_date="2021-05-01",
            last_updated="2021-05-02",
            value=42,
        ),
    ]
    for m in measures:
        db.session.add(m)
    start_date = "2021-05-01T00:00:01"
    end_date = "2021-05-03T00:00:00"
    agg = aggregation.aggregate_measures_from_db(
        measure_name, start_date, end_date
    )
    assert len(agg) == 1
    # The first measure is filtered out because of the start date
    assert agg[0].count == 2

    m = RawMeasure(
        measure_name=measure_name,
        start_date="2021-05-01",
        last_updated="2021-05-03T00:00:01",
        value=42,
    )
    db.session.add(m)
    agg = aggregation.aggregate_measures_from_db(
        measure_name, start_date, end_date
    )
    assert len(agg) == 1
    # The last measure is filtered out because of the last date
    assert agg[0].count == 2

    start_date = "2021-05-01T00:00:00"
    end_date = "2021-05-03T00:00:01"
    agg = aggregation.aggregate_measures_from_db(
        measure_name, start_date, end_date
    )
    assert len(agg) == 1
    # All measures are included
    assert agg[0].count == 4

    db.session.rollback()


def test_dates_bounds():
    # No raw measure for this indicator
    m_def = MeasureDefinition.query_by_name("energy-consumption-daily")
    start_date, end_date = aggregation.find_dates_bounds(m_def)
    assert start_date is None
    assert end_date is None

    # Raw measures exist but no aggregation date
    m_def = MeasureDefinition.query_by_name("connection-count-daily")
    start_date, end_date = aggregation.find_dates_bounds(m_def)
    assert start_date == datetime.min
    assert end_date == datetime(2021, 5, 3, 0, 0, 0, 4000)

    # Raw measures exist with aggregation date
    m_date = datetime(2021, 5, 1, 0, 0, 0, 0)
    agg_date = AggregationDate(
        measure_definition_id=1,
        last_aggregated_measure_date=m_date,
    )
    db.session.add(agg_date)
    start_date, end_date = aggregation.find_dates_bounds(m_def)
    assert start_date == m_date
    assert end_date == datetime(2021, 5, 3, 0, 0, 0, 4000)

    db.session.rollback()


def test_new_aggregation_date():
    m_def = MeasureDefinition.query_by_name("connection-count-daily")
    date = datetime(2021, 5, 1, 0, 0, 0, 0)
    agg_date = aggregation.get_new_aggregation_date(m_def, date)
    assert agg_date.measure_definition_id == 1
    assert agg_date.last_aggregated_measure_date == date

    db.session.add(agg_date)
    date = datetime(2021, 5, 2, 0, 0, 0, 0)
    agg_date = aggregation.get_new_aggregation_date(m_def, date)
    assert agg_date.measure_definition_id == 1
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
    values_g1 = [5, 10, 10, 15]
    curr_agg = Aggregation(
        measure_name=measure_name,
        start_date=start_date,
        sum=np.sum(values_g1),
        count=len(values_g1),
        count_not_zero=len(np.nonzero(values_g1)[0]),
        min=np.min(values_g1),
        max=np.max(values_g1),
        avg=np.mean(values_g1),
        std=np.std(values_g1, ddof=1),
    )
    values_g2 = [0, 6, 20]
    new_agg = Aggregation(
        measure_name=measure_name,
        start_date=start_date,
        sum=np.sum(values_g2),
        count=len(values_g2),
        count_not_zero=len(np.nonzero(values_g2)[0]),
        min=np.min(values_g2),
        max=np.max(values_g2),
        avg=np.mean(values_g2),
        std=np.std(values_g2, ddof=1),
    )
    agg = aggregation.compute_partial_aggregates(
        measure_name, curr_agg, new_agg
    )
    assert agg.count == len(values_g1) + len(values_g2)
    assert agg.count_not_zero == len(np.nonzero(values_g1)[0]) + len(
        np.nonzero(values_g2)[0]
    )
    assert agg.sum == np.sum(values_g1) + np.sum(values_g2)
    assert agg.min == np.min(values_g1 + values_g2)
    assert agg.max == np.max(values_g1 + values_g2)
    assert agg.avg == np.mean(values_g1 + values_g2)
    assert round(agg.std, 4) == round(np.std(values_g1 + values_g2, ddof=1), 4)


def test_compute_grouped_std():

    values = [0, 5, 10, 10, 15, 20, 20]
    val_g1 = [0, 10, 20]
    val_g2 = [5, 10, 15, 20]

    std = np.std(values, ddof=1)
    std_g1 = np.std(val_g1, ddof=1)
    std_g2 = np.std(val_g2, ddof=1)

    agg1 = Aggregation(count=len(val_g1), std=std_g1, avg=np.mean(val_g1))
    agg2 = Aggregation(count=len(val_g2), std=std_g2, avg=np.mean(val_g2))
    global_mean = np.mean(values)

    new_std = aggregation.compute_grouped_std(agg1, agg2, global_mean)

    assert round(new_std, 4) == round(std, 4)


def test_aggregation_execution():
    m_def = MeasureDefinition.query_by_name("connection-count-daily")
    agg, date = aggregation.aggregate_raw_measures(m_def)
    assert len(agg) == 3
    assert date == datetime(2021, 5, 3, 0, 0, 0, 4000)

    # No new measure
    agg, date = aggregation.aggregate_raw_measures(m_def)
    assert agg is None
    assert date is None

    # New measure is aggregated
    m = RawMeasure(
        measure_name="connection-count-daily",
        value=42,
        start_date="2021-05-02",
        group1='{"device": "mobile"}',
    )
    db.session.add(m)
    db.session.commit()
    agg, date = aggregation.aggregate_raw_measures(m_def)
    assert len(agg) == 1

    # Execution date is too close
    m = RawMeasure(
        measure_name="connection-count-daily",
        value=42,
        start_date="2021-05-03",
        group1='{"device": "mobile"}',
    )
    db.session.add(m)
    db.session.commit()
    agg, date = aggregation.aggregate_raw_measures(m_def)
    assert agg is None
    assert date is None

    # Force execution of last 2 inserts
    agg_date = AggregationDate.query_by_name(m_def.name)
    agg_date.last_aggregated_measure_date = datetime.now() - timedelta(days=1)
    db.session.add(m)
    db.session.commit()
    agg, date = aggregation.aggregate_raw_measures(m_def)
    assert len(agg) == 2
    assert agg[0].start_date == datetime(2021, 5, 2)
    assert agg[1].start_date == datetime(2021, 5, 3)
