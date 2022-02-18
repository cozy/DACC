from datetime import datetime
from dacc import db
from dacc.models import MeasureDefinition, RawMeasure, Aggregation
from dacc.purge import purge_measures
from dacc.aggregation import aggregate_raw_measures
from tests.fixtures import fixtures


def insert_dummy(n_measures, n_days, date, name):
    fixtures.insert_random_raw_measures(
        n_measures,
        n_days,
        date,
        name,
        "dummy-app",
        group1={"key1": 1},
        group2={"key2": 2},
        group3={"key3": 3},
    )


def insert_definition(name, with_quartiles=False):
    m_def = MeasureDefinition(
        name=name,
        aggregation_threshold=2,
        group1_key="key1",
        group2_key="key2",
        group3_key="key3",
        with_quartiles=with_quartiles,
    )
    db.session.add(m_def)
    return m_def


def get_aggregate(measure_name, start_date):
    measure = RawMeasure(
        start_date=start_date,
        created_by="dummy-app",
        group1={"key1": 1},
        group2={"key2": 2},
        group3={"key3": 3},
    )
    return Aggregation.query_aggregate_by_measure(measure_name, measure)


def test_purge_measures():
    dummy_name1 = "dummy1"
    dummy_name2 = "dummy2"
    dummy_name3 = "dummy3"

    m_def_1 = insert_definition(dummy_name1)
    m_def_2 = insert_definition(dummy_name2)
    m_def_3 = insert_definition(dummy_name3)
    insert_dummy(10, 1, "2022-01-01", dummy_name1)
    insert_dummy(20, 1, "2022-01-01", dummy_name2)
    insert_dummy(5, 1, "2022-01-01", dummy_name3)

    aggregate_raw_measures(m_def_1)
    aggregate_raw_measures(m_def_2)

    assert len(RawMeasure.query_by_name(dummy_name1)) == 10
    assert len(RawMeasure.query_by_name(dummy_name2)) == 20
    assert len(RawMeasure.query_by_name(dummy_name3)) == 5

    agg_1 = get_aggregate(dummy_name1, "2022-01-01")
    agg_2 = get_aggregate(dummy_name1, "2022-01-01")
    agg_3 = get_aggregate(dummy_name1, "2022-01-01")
    assert agg_1.last_raw_measures_purged is None
    assert agg_2.last_raw_measures_purged is None
    assert agg_2.last_raw_measures_purged is None

    purge_date = datetime.now()
    print("date : {}".format(purge_date))

    # Purge all measures with date
    purge_measures(m_def_1, purge_date)
    assert len(RawMeasure.query_by_name(dummy_name1)) == 0

    # Purge half of measures with date
    m_dummy_name2 = RawMeasure.query_by_name(dummy_name2)
    assert len(m_dummy_name2) == 20
    purge_date = m_dummy_name2[9].last_updated
    purge_measures(m_def_2, purge_date)
    assert len(RawMeasure.query_by_name(dummy_name2)) == 10

    # If no aggregation date exists, nothing will be purged
    purge_date = datetime.now()
    purge_measures(m_def_3, purge_date)
    assert len(RawMeasure.query_by_name(dummy_name3)) == 5

    # Do not purge when there are non-aggregated measures
    aggregate_raw_measures(m_def_3)
    insert_dummy(10, 1, "2022-01-01", dummy_name3)
    purge_measures(m_def_3, purge_date)
    assert len(RawMeasure.query_by_name(dummy_name3)) == 15

    # Purge measures based on last aggregation date
    insert_dummy(10, 1, "2022-01-01", dummy_name1)

    aggregate_raw_measures(m_def_1, force=True)
    aggregate_raw_measures(m_def_2, force=True)

    purge_measures(m_def_1)
    purge_measures(m_def_2)
    assert len(RawMeasure.query_by_name(dummy_name1)) == 0
    assert len(RawMeasure.query_by_name(dummy_name2)) == 0

    # Non-aggregated measures remain
    purge_measures(m_def_3)
    assert len(RawMeasure.query_by_name(dummy_name3)) == 10

    agg_1 = get_aggregate(dummy_name1, "2022-01-01")
    agg_2 = get_aggregate(dummy_name1, "2022-01-01")
    agg_3 = get_aggregate(dummy_name1, "2022-01-01")
    assert agg_1.last_raw_measures_purged is not None
    assert agg_2.last_raw_measures_purged is not None
    assert agg_3.last_raw_measures_purged is not None


def test_purge_measures_with_quartiles():
    dummy_quartiles = "dummy_quartiles"
    dummy_not_quartiles = "dummy_not_quartiles"

    m_def_quartiles = insert_definition(dummy_quartiles, with_quartiles=True)
    m_def_not_quartiles = insert_definition(
        dummy_not_quartiles, with_quartiles=False
    )

    insert_dummy(20, 1, "2022-01-01", dummy_quartiles)
    insert_dummy(20, 1, "2022-01-01", dummy_not_quartiles)

    aggregate_raw_measures(m_def_quartiles)
    aggregate_raw_measures(m_def_not_quartiles)

    # Measures are not purged, as the retention date is not reached
    assert len(RawMeasure.query_by_name(dummy_quartiles)) == 20
    assert len(RawMeasure.query_by_name(dummy_not_quartiles)) == 20

    agg_q = get_aggregate(dummy_quartiles, "2022-01-01")
    agg_nq = get_aggregate(dummy_not_quartiles, "2022-01-01")
    assert agg_q.last_raw_measures_purged is None
    assert agg_nq.last_raw_measures_purged is None

    # Simulate old inserts
    db.session.query(RawMeasure).filter(
        RawMeasure.measure_name == dummy_quartiles
    ).update({"last_updated": "2020-01-01"})

    # Measures are now purged
    purge_measures(m_def_quartiles)
    assert len(RawMeasure.query_by_name(dummy_quartiles)) == 0
    assert len(RawMeasure.query_by_name(dummy_not_quartiles)) == 20
    agg_q = get_aggregate(dummy_quartiles, "2022-01-01")
    agg_nq = get_aggregate(dummy_not_quartiles, "2022-01-01")
    assert agg_q.last_raw_measures_purged is not None
    assert agg_nq.last_raw_measures_purged is None
