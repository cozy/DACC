from dacc.models import (
    RawMeasures,
    Aggregation,
    AggregationDates,
    MeasuresDefinition,
)
from dacc import db
from sqlalchemy import func
from datetime import datetime
from copy import copy


def query_measures_to_aggregate_by_name(measure_name, start_date, end_date):
    if start_date is None:
        start_date = datetime.min
    if end_date is None:
        end_date = datetime.now()
    return (
        db.session.query(
            RawMeasures.created_by,
            RawMeasures.start_date,
            RawMeasures.group1,
            RawMeasures.group2,
            RawMeasures.group3,
            func.count(RawMeasures.value).label("count"),
            func.sum(RawMeasures.value).label("sum"),
            func.min(RawMeasures.value).label("min"),
            func.max(RawMeasures.value).label("max"),
            func.avg(RawMeasures.value).label("avg"),
        )
        .filter(
            RawMeasures.measure_name == measure_name,
            RawMeasures.last_updated > start_date,
            RawMeasures.last_updated < end_date,
        )
        .group_by(
            RawMeasures.created_by,
            RawMeasures.start_date,
            RawMeasures.group1,
            RawMeasures.group2,
            RawMeasures.group3,
        )
        .all()
    )


def get_new_aggregation_date(measure_name, date):
    agg_date = AggregationDates.query_by_name(measure_name)
    if agg_date is None:
        m_def = MeasuresDefinition.query_by_name(measure_name)
        if m_def is None:
            return None
        return AggregationDates(
            measures_definition_id=m_def.id,
            last_aggregated_measure_date=date,
        )
    else:
        agg_date.last_aggregated_measure_date = date
        return agg_date


def find_time_interval(measure_name):
    agg_date = AggregationDates.query_by_name(measure_name)
    if agg_date is None:
        start_date = datetime.min
    else:
        start_date = agg_date.last_aggregated_measure_date

    m_most_recent_date = RawMeasures.query_most_recent_date(
        measure_name, start_date
    )
    if m_most_recent_date is None:
        return (None, None)
    end_date = m_most_recent_date[0]
    return start_date, end_date


def compute_partial_aggregates(current_agg, new_agg):
    if current_agg.measure_name != new_agg.measure_name:
        raise Exception(
            "Cannot compute aggregation on different measures: {} - {}".format(
                current_agg.measure_name, new_agg.measure_name
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
    agg.sum += new_agg.sum
    agg.max = max(agg.max, new_agg.max)
    agg.min = min(agg.min, new_agg.min)
    agg.avg = (
        agg.avg * current_agg.count + new_agg.avg * new_agg.count
    ) / agg.count

    return agg


# TODO: this could probably be improved, typically by using a view to
# get the relevant tuples and use its output to perform the aggregation.
# This would avoid to perform 2 disinct queries on the raw_measures database.
def aggregate_raw_measures(measure_name):
    try:
        start_date, end_date = find_time_interval(measure_name)
        if end_date is None:
            # No measures to aggregate
            return

        grouped_measures = query_measures_to_aggregate_by_name(
            measure_name, start_date, end_date
        )
        for gm in grouped_measures:
            agg = Aggregation.query_aggregate_by_measure(gm)
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
                    min=gm.min,
                    max=gm.max,
                    avg=gm.avg,
                )
                db.session.add(agg)
            else:
                # This will be an update in the Aggregation table
                agg = compute_partial_aggregates(agg, gm)

        agg_date = get_new_aggregation_date(measure_name, end_date)
        if agg_date is None:
            raise Exception(
                "No measure definition found for {}".format(measure_name)
            )
        db.session.add(agg_date)
        db.session.commit()

    except Exception as err:
        print("Error while aggregating: " + repr(err))
