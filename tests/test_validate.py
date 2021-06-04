import pytest
from dacc import validate


def assert_exception(m, exception_value):
    with pytest.raises(Exception) as e_info:
        validate.check_incoming_raw_measure(m)
    assert exception_value in str(e_info.value)


def test_check_incoming_raw_measure():
    m = {"value": 42}
    assert_exception(m, "A measure name must be given")

    m = {"measureName": "dummy", "value": 42}
    assert_exception(m, "No measure definition found for dummy")

    m = {"measureName": "connection-count-daily"}
    assert_exception(m, "A value must be given")

    m = {"measureName": "connection-count-daily", "value": "not-a-number"}
    assert_exception(m, "value type is incorrect, it must be a number")

    m = {"measureName": "connection-count-daily", "value": 42}
    assert_exception(m, "A start date must be given")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "not-a-date",
    }
    assert_exception(m, "startDate type is incorrect, it must be a date")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "groups": ["dummy"],
    }
    assert_exception(m, "groups format is incorrect")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "groups": [{"dummy": "dummy"}, {"dummy"}],
    }
    assert_exception(m, "groups format is incorrect")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "groups": [{"dummy": "dummy"}],
    }
    assert_exception(m, "Group key does not match measure definition")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "groups": [{"device": "dummy"}, {"dummy": "dummy"}],
    }
    assert_exception(m, "Group key does not match measure definition")

    m = {
        "measureName": "connection-count-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "groups": [{"device": "desktop"}],
    }
    assert validate.check_incoming_raw_measure(m) is True

    m = {
        "measureName": "konnector-event-daily",
        "value": 42,
        "startDate": "2021-05-01",
        "groups": [
            {"slug": "enedis"},
            {"event_type": "connexion"},
            {"status": "success"},
        ],
    }
    assert validate.check_incoming_raw_measure(m) is True
