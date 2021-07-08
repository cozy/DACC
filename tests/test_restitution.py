from dacc import db, restitution, aggregation
from dacc.models import MeasureDefinition
from tests.fixtures import fixtures
from dateutil.parser import parse


def insert_dummy(n_measures, n_days, date, created_by="ecolyo"):
    fixtures.insert_random_raw_measures(
        n_measures,
        n_days,
        date,
        "dummy-restitute",
        created_by,
        group1={"key1": 1},
        group2={"key2": 2},
        group3={"key3": 3},
    )


def test_restitute_aggregated_results():
    m_def = MeasureDefinition(
        name="dummy-restitute",
        aggregation_threshold=5,
        group1_key="key1",
        group2_key="key2",
        group3_key="key3",
    )
    db.session.add(m_def)

    insert_dummy(10, 1, "2021-05-01")
    aggregation.aggregate_raw_measures(m_def, force=True)

    p = {
        "measureName": "dummy",
        "startDate": "2021-05-01",
        "endDate": "2021-06-01",
    }

    res = restitution.get_aggregated_results(p)
    assert len(res) == 1
    assert res[0]["startDate"] == parse("2021-05-01")
    assert res[0]["count"] == 10
    assert res[0]["measureName"] == "dummy-restitute"
    assert res[0]["createdBy"] == "ecolyo"
    assert "sum" in res[0]
    assert "countNotZero" in res[0]
    assert "min" in res[0]
    assert "max" in res[0]
    assert "avg" in res[0]
    assert "std" in res[0]

    # Not enough contributions to get results
    insert_dummy(4, 1, "2021-05-02")
    aggregation.aggregate_raw_measures(m_def, force=True)

    res = restitution.get_aggregated_results(p)
    assert len(res) == 1
    assert res[0]["startDate"] == parse("2021-05-01")

    # Add enough contributions to get results
    insert_dummy(1, 1, "2021-05-02")
    aggregation.aggregate_raw_measures(m_def, force=True)

    res = restitution.get_aggregated_results(p)
    assert len(res) == 2
    assert res[1]["startDate"] == parse("2021-05-02")
    assert res[1]["count"] == 5

    # Add measures before and after date range
    insert_dummy(10, 1, "2021-04-30")
    insert_dummy(10, 1, "2021-06-01")
    aggregation.aggregate_raw_measures(m_def, force=True)

    res = restitution.get_aggregated_results(p)
    assert len(res) == 2

    # Add measures on the boundaries of date range
    insert_dummy(10, 1, "2021-05-01T00:00:00")
    insert_dummy(10, 1, "2021-05-30T23:59:59")
    aggregation.aggregate_raw_measures(m_def, force=True)

    res = restitution.get_aggregated_results(p)
    assert len(res) == 3
    assert res[0]["count"] == 20
    assert res[1]["count"] == 5
    assert res[2]["count"] == 10

    # Filter on specific app
    insert_dummy(10, 1, "2021-05-01", created_by="ecolyoyo")
    aggregation.aggregate_raw_measures(m_def, force=True)
    p = {
        "measureName": "dummy-restitute",
        "startDate": "2021-05-01",
        "endDate": "2021-06-01",
        "createdBy": "ecolyoyo",
    }
    res = restitution.get_aggregated_results(p)
    assert len(res) == 1
    assert res[0]["count"] == 10
