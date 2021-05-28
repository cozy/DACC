from dacc.models import RawMeasures, Aggregation, AggregationDates
from dacc import db
from sqlalchemy import func
from datetime import datetime


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
            func.sum(RawMeasures.value).label("sum"),
            func.count(RawMeasures.value).label("count"),
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


# TODO: this could probably be improved, typically by using a view to
# get the relevant tuples and use its output to perform the aggregation.
# This would avoid to perform 2 disinct queries on the raw_measures database.
def aggregate_raw_measures(measure_name):
    try:
        agg_dates_rows = AggregationDates.query_last_date_by_name(measure_name)
        if len(agg_dates_rows) > 0:
            start_date = agg_dates_rows[0].last_aggregated_measure_date
        else:
            start_date = datetime.min

        m_dates_rows = RawMeasures.query_most_recent_date(
            measure_name, start_date
        )
        if len(m_dates_rows) > 0:
            end_date = m_dates_rows[0].last_updated
        else:
            end_date = datetime.min

        grouped_measures = query_measures_to_aggregate_by_name(
            measure_name, start_date, end_date
        )
        for m in grouped_measures:
            agg = Aggregation(
                measure_name=measure_name,
                start_date=m.start_date,
                created_by=m.created_by,
                group1=m.group1,
                group2=m.group2,
                group3=m.group3,
                sum=m.sum,
                count=m.count,
                min=m.min,
                max=m.max,
                average=m.avg,
            )
            db.session.add(agg)
            db.session.commit()
    except Exception as err:
        print("Error while aggregating: " + repr(err))
