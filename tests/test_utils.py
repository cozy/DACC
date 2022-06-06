from dacc import utils
from dateutil.parser import parse


def test_is_date_interval_higher():
    s_date = parse("2021-05-01T00:00:00")
    e_date = parse("2021-05-01T00:00:00")
    period = "day"
    assert utils.is_dates_interval_higher(s_date, e_date, period) is False
    e_date = parse("2021-05-01T23:59:59")
    assert utils.is_dates_interval_higher(s_date, e_date, period) is False
    e_date = parse("2021-05-02")
    assert utils.is_dates_interval_higher(s_date, e_date, period) is True

    period = "week"
    assert utils.is_dates_interval_higher(s_date, e_date, period) is False
    e_date = parse("2021-05-08")
    assert utils.is_dates_interval_higher(s_date, e_date, period) is True

    period = "month"
    assert utils.is_dates_interval_higher(s_date, e_date, period) is False
    e_date = parse("2021-06-01")
    assert utils.is_dates_interval_higher(s_date, e_date, period) is True


def test_to_camel_case():
    str1 = "my_string"
    assert utils.to_camel_case(str1) == "myString"

    str2 = "my_long_string_with_lot_of_stuff"
    assert utils.to_camel_case(str2) == "myLongStringWithLotOfStuff"

    str3 = "simple"
    assert utils.to_camel_case(str3) == "simple"

    str4 = "alreadyCamelCase"
    assert utils.to_camel_case(str4) == "alreadyCamelCase"
