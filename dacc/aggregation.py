from dacc.models import (
    RawMeasure,
    Aggregation,
    AggregationDate,
    MeasureDefinition,
)
from dacc import db
from sqlalchemy import func
from datetime import datetime
from copy import copy
import math


def query_measures_to_aggregate_by_name(measure_name, start_date, end_date):
    if start_date is None:
        start_date = datetime.min
    if end_date is None:
        end_date = datetime.now()
    return (
        db.session.query(
            RawMeasure.created_by,
            RawMeasure.start_date,
            RawMeasure.group1,
            RawMeasure.group2,
            RawMeasure.group3,
            func.count(RawMeasure.value).label("count"),
            func.count(func.nullif(RawMeasure.value, 0)).label(
                "count_not_zero"
            ),
            func.sum(RawMeasure.value).label("sum"),
            func.min(RawMeasure.value).label("min"),
            func.max(RawMeasure.value).label("max"),
            func.avg(RawMeasure.value).label("avg"),
            func.stddev(RawMeasure.value).label("std"),
        )
        .filter(
            RawMeasure.measure_name == measure_name,
            RawMeasure.last_updated > start_date,
            RawMeasure.last_updated <= end_date,
        )
        .group_by(
            RawMeasure.created_by,
            RawMeasure.start_date,
            RawMeasure.group1,
            RawMeasure.group2,
            RawMeasure.group3,
        )
        .all()
    )


def get_new_aggregation_date(measure_name, date):
    agg_date = AggregationDate.query_by_name(measure_name)
    if agg_date is None:
        m_def = MeasureDefinition.query_by_name(measure_name)
        if m_def is None:
            return None
        return AggregationDate(
            measure_definition_id=m_def.id,
            last_aggregated_measure_date=date,
        )
    else:
        agg_date.last_aggregated_measure_date = date
        return agg_date


def find_time_interval(measure_name):
    agg_date = AggregationDate.query_by_name(measure_name)
    if agg_date is None:
        start_date = datetime.min
    else:
        start_date = agg_date.last_aggregated_measure_date

    m_most_recent_date = RawMeasure.query_most_recent_date(
        measure_name, start_date
    )
    if m_most_recent_date is None:
        return (None, None)
    end_date = m_most_recent_date[0]
    return start_date, end_date


def compute_grouped_std(current_agg, new_agg, global_mean):
    """Compute grouped sampled standard deviation, from a current aggregation
        and a new one.
        See https://stackoverflow.com/questions/7753002/adding-combining-standard-deviations

    Args:
        current_agg ([Aggregation]): [the existing aggregate]
        new_agg ([Aggregation]): [the newly computed aggregate]
        global_mean ([float]): [mean of the whole measures]

    Returns:
        [float]: [sampled standard deviation]
    """
    n1 = current_agg.count
    n2 = new_agg.count
    v1 = current_agg.std ** 2
    v2 = new_agg.std ** 2
    m1 = current_agg.avg
    m2 = new_agg.avg
    M = global_mean

    s1 = (n1 - 1) * v1 + (n2 - 1) * v2
    s2 = n1 * (m1 - M) ** 2 + n2 * (m2 - M) ** 2

    v = (s1 + s2) / (n1 + n2 - 1)  # Compute global variance
    return math.sqrt(v)  # return std


def compute_partial_aggregates(measure_name, current_agg, new_agg):
    if current_agg.measure_name != measure_name:
        raise Exception(
            "Cannot compute aggregation on different measures: {} - {}".format(
                current_agg.measure_name, measure_name
            )
        )
    if current_agg.start_date != new_agg.start_date:
        raise Exception(
            "Cannot compute aggregation on different dates: {} - {}".format(
                current_agg.start_date, new_agg.start_date
            )
        )

    agg = copy(current_agg)
    agg.count += new_agg.count
    agg.count_not_zero += new_agg.count_not_zero
    agg.sum += new_agg.sum
    agg.min = min(agg.min, new_agg.min)
    agg.max = max(agg.max, new_agg.max)
    # XXX - The mean could be computed on restitution instead of storing it.
    agg.avg = (current_agg.sum + new_agg.sum) / agg.count
    # XXX - Using variance might be more precise to avoid float rounds
    # and std computed on restitution
    agg.std = compute_grouped_std(current_agg, new_agg, agg.avg)

    return agg


# TODO: this could probably be improved, typically by using a view to
# get the relevant tuples and use its output to perform the aggregation.
# This would avoid to perform 2 disinct queries on the raw_measures database.
def aggregate_raw_measures(measure_name):
    try:
        start_date, end_date = find_time_interval(measure_name)
        if end_date is None:
            # No measures to aggregate
            return (None, None)

        grouped_measures = query_measures_to_aggregate_by_name(
            measure_name, start_date, end_date
        )
        for gm in grouped_measures:
            agg = Aggregation.query_aggregate_by_measure(measure_name, gm)
            if agg is None:
                # This will be an insert in the Aggregation table
                agg = Aggregation(
                    measure_name=measure_name,
                    start_date=gm.start_date,
                    created_by=gm.created_by,
                    group1=gm.group1,
                    group2=gm.group2,
                    group3=gm.group3,
                    sum=gm.sum,
                    count=gm.count,
                    count_not_zero=gm.count_not_zero,
                    min=gm.min,
                    max=gm.max,
                    avg=gm.avg,
                    std=gm.std,
                )
                db.session.add(agg)
            else:
                # This will be an update in the Aggregation table
                # XXX - This might be improved by avoiding a new query
                agg = compute_partial_aggregates(measure_name, agg, gm)
                db.session.query(Aggregation).filter(
                    Aggregation.id == agg.id
                ).update(
                    {
                        "sum": agg.sum,
                        "count": agg.count,
                        "count_not_zero": agg.count_not_zero,
                        "min": agg.min,
                        "max": agg.max,
                        "avg": agg.avg,
                        "std": agg.std,
                    },
                )

        agg_date = get_new_aggregation_date(measure_name, end_date)

        if agg_date is None:
            raise Exception(
                "No measure definition found for {}".format(measure_name)
            )
        db.session.add(agg_date)
        db.session.commit()
        return grouped_measures, agg_date.last_aggregated_measure_date

    except Exception as err:
        print("Error while aggregating: " + repr(err))
