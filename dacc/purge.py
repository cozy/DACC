from dacc import db
from dacc.models import (
    RawMeasure,
    AggregationDate,
    MeasureDefinition,
    Aggregation,
)
from dacc.aggregation import aggregation_query
from datetime import datetime


def has_not_aggregated_measures(
    m_definition: MeasureDefinition,
    last_aggregated_date: datetime,
    purge_date: datetime,
):
    """Returns whether or not some raw measures are not aggregated yet,
    compared to the given `purge_date`.

    Args:
        m_definition (MeasureDefinition): The measure definition
        last_aggregated_date (datetime): The date of the last aggregation
        purge_date (datetime): The purge date

    Returns:
        Bool: True if some measures are more recent than the last aggregation.
    """
    if purge_date <= last_aggregated_date:
        return False
    measures_more_recent_than_date = (
        db.session.query(RawMeasure)
        .filter(RawMeasure.measure_name == m_definition.name)
        .filter(RawMeasure.last_updated > purge_date)
        .all()
    )

    return len(measures_more_recent_than_date) > 0


def get_quartiles_filter(m_definition: MeasureDefinition):
    if m_definition.with_quartiles:
        max_days = m_definition.max_days_to_update_quartile
        return [datetime.now() > RawMeasure.max_retention_date(max_days)]
    return []


def get_filters_measures(
    m_definition: MeasureDefinition, purge_date: datetime
):
    filters = [
        RawMeasure.measure_name == m_definition.name,
        RawMeasure.last_updated <= purge_date,
    ]
    quartile_filter = get_quartiles_filter(m_definition)
    print("quartile filter : {}".format(quartile_filter))
    if len(quartile_filter) > 0:
        return filters + quartile_filter
    return filters


def update_impacted_aggregates(
    m_definition: MeasureDefinition, grouped_measures
):
    for gm in grouped_measures:
        agg = Aggregation.query_aggregate_by_measure(m_definition.name, gm)
        db.session.query(Aggregation).filter(Aggregation.id == agg.id).update(
            {"last_raw_measures_purged": datetime.now()}
        )

    return len(grouped_measures)


def query_grouped_measures(
    m_definition: MeasureDefinition, purge_date: datetime
):
    query_args = [
        RawMeasure.created_by,
        RawMeasure.start_date,
        RawMeasure.group1,
        RawMeasure.group2,
        RawMeasure.group3,
    ]
    filters_args = get_filters_measures(m_definition, purge_date)
    return aggregation_query(
        m_definition,
        query_args,
        filters_args,
    )


def query_measures_to_purge(
    m_definition: MeasureDefinition, purge_date: datetime
):
    filter_args = get_filters_measures(m_definition, purge_date)
    query = db.session.query(RawMeasure).filter(*filter_args)
    return query


def purge_quartiles(m_definition: MeasureDefinition, purge_date: datetime):
    measures = query_measures_to_purge(m_definition, purge_date)
    measures.delete()


def purge_measures(
    m_definition: MeasureDefinition, purge_date: datetime = None
):
    """Purge the raw measures for the given definition.

    All the raw measures with a last_updated date inferior to the purge
    date should be erased, except for the following cases:
     - Some raw measures are not aggregated yet.
     - The definition includes quartiles and some measures do not reach the
       `max_days_to_update_quartile` threshold..
    Furthermore, each impacted aggregate updates its `last_raw_measures_purged`
    date.

    When no purge_date is given, the `last_aggregated_measure_date` is used.

    Args:
        m_definition (MeasureDefinition): The measure definition
        purge_date (datetime, optional): The purge date. Defaults to None.
    """

    agg_date = AggregationDate.query_by_name(m_definition.name)
    if agg_date is None:
        print(
            "No aggregation date for {}. Nothing to purge.".format(
                m_definition.name
            )
        )
        return

    if purge_date is None:
        purge_date = agg_date.last_aggregated_measure_date
    else:
        # Prevent any non-aggregated measure to be purged
        if has_not_aggregated_measures(
            m_definition,
            agg_date.last_aggregated_measure_date,
            purge_date,
        ):
            print("This would remove non-aggregated measures. Abort.")
            return

    # Get grouped measures before deletion
    grouped_measures = query_grouped_measures(m_definition, purge_date)

    # Delete raw measures
    n_deleted_measures = query_measures_to_purge(
        m_definition, purge_date
    ).delete()
    print(
        "{} raw measures deleted for {}".format(
            n_deleted_measures, m_definition.name
        )
    )
    # if n_deleted_measures < 1:
    #     return

    # Update impacted aggregates
    n_updated_aggregates = update_impacted_aggregates(
        m_definition, grouped_measures
    )
    print(
        "{} updated aggregates with purged date".format(n_updated_aggregates)
    )

    db.session.commit()
