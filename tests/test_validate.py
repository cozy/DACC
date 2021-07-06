import pytest
from dacc import validate


def assert_raw_measure_exception(m, exception_value):
    with pytest.raises(Exception) as e_info:
        validate.check_incoming_raw_measure(m)
    assert exception_value in str(e_info.value)


def test_check_incoming_raw_measure():
    m = None
    assert_raw_measure_exception(m, "The measure cannot be empty")

    m = {"value": 42}
    assert_raw_measure_exception(m, "A measure name must be given")

    m = {"measureName": "fake-dummy", "value": 42}
    assert_raw_measure_exception(
        m, "No measure definition found for: fake-dummy"
    )

    m = {"measureName": "connection-count-daily"}
    assert_raw_measure_exception(m, "A value must be given")

    m = {"measureName": "connection-count-daily", "value": "not-a-number"}
    assert_raw_measure_exception(
        m, "value type is incorrect, it must be a number"
    )

    m = {"measureName": "connection-count-daily", "value": 42}
    assert_raw_measure_exception(m, "startDate must be given")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "not-a-date",
    }
    assert_raw_measure_exception(
        m, "startDate type is incorrect, it must be a date"
    )

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "group1": ["dummy"],
    }
    assert_raw_measure_exception(m, "groups format is incorrect")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "group1": {"dummy": "dummy"},
        "group2": {"dummy"},
    }
    assert_raw_measure_exception(m, "groups format is incorrect")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "group1": {"dummy": "dummy"},
    }
    assert_raw_measure_exception(
        m, "Group1 key does not match measure definition"
    )

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "group1": {"device": "dummy"},
        "group2": {"dummy": "dummy"},
    }
    assert_raw_measure_exception(
        m, "Group2 key does not match measure definition"
    )

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "group1": {"device": "desktop"},
    }
    assert validate.check_incoming_raw_measure(m) is True

    m = {
        "measureName": "konnector-event-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "group1": {"slug": "enedis"},
        "group2": {"event_type": "connexion"},
        "group3": {"status": "success"},
    }
    assert validate.check_incoming_raw_measure(m) is True


def assert_restitution_exception(m, exception_value):
    with pytest.raises(Exception) as e_info:
        validate.check_restitution_params(m)
    assert exception_value in str(e_info.value)


def test_check_restitution_params():
    p = None
    assert_restitution_exception(p, "The params cannot be empty")

    p = {"startDate": "2021-05-01"}
    assert_restitution_exception(p, "A measure name must be given")

    p = {"measureName": "fake-dummy"}
    assert_restitution_exception(
        p, "No measure definition found for: fake-dummy"
    )

    p = {"measureName": "connection-count-daily"}
    assert_restitution_exception(p, "startDate must be given")

    p = {
        "measureName": "connection-count-daily",
        "startDate": "not-a-date",
    }
    assert_restitution_exception(
        p, "startDate type is incorrect, it must be a date"
    )

    p = {"measureName": "connection-count-daily", "startDate": "2021-05-01"}
    assert_restitution_exception(p, "endDate must be given")

    p = {
        "measureName": "connection-count-daily",
        "startDate": "2021-05-01",
        "endDate": "not-a-date",
    }
    assert_restitution_exception(
        p, "endDate type is incorrect, it must be a date"
    )

    p = {
        "measureName": "connection-count-daily",
        "startDate": "2021-05-01",
        "endDate": "2021-06-01",
    }
    assert validate.check_restitution_params(p) is True
