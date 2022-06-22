from dacc.models import (
    RawMeasure,
    Aggregation,
    AggregationDate,
    MeasureDefinition,
    RefusedRawMeasure,
    tuple_as_dict,
)
from dacc import db, validate
from sqlalchemy import func, bindparam, update
from datetime import datetime
from copy import copy
import math
import logging
import time
import numpy as np
import json
from typing import Any, List


def aggregation_query(
    m_definition: MeasureDefinition,
    query_args: list,
    filter_args: list,
):
    """Execute aggregation query on database

    Args:
        m_definition (MeasureDefinition): The measure definition
        query_args (list): The query (select) arguments
        filter_args (list): The filter argument

    Returns:
        list(RawMeasure): the aggregated measures
    """
    return (
        db.session.query(*query_args)
        .filter(*filter_args)
        .group_by(
            RawMeasure.created_by,
            RawMeasure.start_date,
            RawMeasure.group1,
            RawMeasure.group2,
            RawMeasure.group3,
        )
        .all()
    )


def get_distributive_funcs_aggregation_query():
    return [
        func.count(RawMeasure.value).label("count"),
        func.count(func.nullif(RawMeasure.value, 0)).label("count_not_zero"),
        func.sum(RawMeasure.value).label("sum"),
        func.min(RawMeasure.value).label("min"),
        func.max(RawMeasure.value).label("max"),
    ]


def get_algebraic_funcs_aggregation_query():
    return [
        func.avg(RawMeasure.value).label("avg"),
        func.coalesce(func.stddev(RawMeasure.value), 0).label("std"),
    ]


def get_quartiles_funcs_aggregation_query():
    return [
        func.percentile_cont(0.5)
        .within_group(RawMeasure.value)
        .label("median"),
        func.percentile_cont(0.25)
        .within_group(RawMeasure.value)
        .label("first_quartile"),
        func.percentile_cont(0.75)
        .within_group(RawMeasure.value)
        .label("third_quartile"),
    ]


def get_all_aggregations_query_args(with_quartiles: bool):
    args = [
        RawMeasure.created_by,
        RawMeasure.start_date,
        RawMeasure.group1,
        RawMeasure.group2,
        RawMeasure.group3,
    ]
    args += get_distributive_funcs_aggregation_query()
    args += get_algebraic_funcs_aggregation_query()
    if with_quartiles:
        args += get_quartiles_funcs_aggregation_query()
    return args


def get_quartiles_aggregation_query_args():
    args = [
        RawMeasure.created_by,
        RawMeasure.start_date,
        RawMeasure.group1,
        RawMeasure.group2,
        RawMeasure.group3,
    ]
    args += get_quartiles_funcs_aggregation_query()
    return args


def get_filters_all_aggregations(
    m_definition: MeasureDefinition, start_date: str, end_date: str
):
    return [
        RawMeasure.measure_name == m_definition.name,
        RawMeasure.last_updated > start_date,
        RawMeasure.last_updated <= end_date,
    ]


def get_filters_quartiles(
    m_definition: MeasureDefinition, existing_agg: Aggregation, end_date: str
):
    return [
        RawMeasure.measure_name == m_definition.name,
        RawMeasure.start_date == existing_agg.start_date,
        RawMeasure.last_updated <= end_date,
        RawMeasure.group1 == existing_agg.group1,
        RawMeasure.group2 == existing_agg.group2,
        RawMeasure.group3 == existing_agg.group3,
    ]


def compute_all_aggregates_from_raw_measures(
    m_definition: MeasureDefinition, start_date: str, end_date: str
):
    """Compute all aggregates on raw measures for the given time interval.

    Args:
        m_definition (MeasureDefinition): The measure definition
        start_date (str): The start date of the query
        end_date (str): The end date of the query

    Returns:
        list(RawMeasure): the aggregated measures
    """
    if start_date is None:
        start_date = datetime.min
    if end_date is None:
        end_date = datetime.now()

    query_args = get_all_aggregations_query_args(m_definition.with_quartiles)
    filter_args = get_filters_all_aggregations(
        m_definition, start_date, end_date
    )

    return aggregation_query(m_definition, query_args, filter_args)


def compute_quartiles_from_raw_measures(
    m_definition: MeasureDefinition, existing_agg: Aggregation, end_date: str
):
    """Compute quartiles aggregates on raw measures for the given time interval.
    It is used to recompute an existing aggregate quartiles.

    Args:
        m_definition (MeasureDefinition): The measure definition
        existing_agg (Aggregation): The existing aggregate to recompute
        end_date (str): The last raw measure date to include.

    Returns:
        RawMeasure: the computed quartiles
    """
    query_args = get_quartiles_aggregation_query_args()
    filters_args = get_filters_quartiles(m_definition, existing_agg, end_date)
    aggs = aggregation_query(
        m_definition,
        query_args,
        filters_args,
    )

    if len(aggs) > 0:
        return aggs[0]
    return None


def get_new_aggregation_date(m_definition: MeasureDefinition, date: str):
    """Update the AggregationDate with the given date.

    Args:
        m_definition (MeasureDefinition): The measure definition
        date (str): The new date to save

    Returns:
        AggregationDate: the updated database entry
    """
    agg_date = AggregationDate.query_by_name(m_definition.name)
    if agg_date is None:
        return AggregationDate(
            measure_definition_id=m_definition.id,
            last_aggregated_measure_date=date,
        )
    else:
        agg_date.last_aggregated_measure_date = date
        return agg_date


def find_dates_bounds(m_definition: MeasureDefinition):
    """Find the starting date and ending date of the measure.

    Args:
        m_definition (MeasureDefinition): The measure definition

    Returns:
        (str, str): A (start_date, end_date) tuple
    """
    agg_date = AggregationDate.query_by_name(m_definition.name)
    if agg_date is None:
        start_date = datetime.min
    else:
        start_date = agg_date.last_aggregated_measure_date

    m_most_recent_date = RawMeasure.query_most_recent_last_updated(
        m_definition.name, start_date
    )
    if m_most_recent_date is None:
        return (None, None)
    end_date = m_most_recent_date[0]
    return start_date, end_date


def compute_grouped_std(
    current_agg: Aggregation, new_agg: Aggregation, global_mean: float
):
    """Compute grouped sampled standard deviation.

    It computes from a current aggregation and a new one.
    See https://stackoverflow.com/questions/7753002/adding-combining-standard-deviations # noqa: E501

    Args:
        current_agg (Aggregation): the existing aggregate
        new_agg (Aggregation): the newly computed aggregate
        global_mean (float): mean of the whole measures

    Returns:
        float: sampled standard deviation
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


def compute_partial_aggregates(
    measure_name: str, current_agg: Aggregation, new_agg: Aggregation
):
    """Compute a partial aggregate based on a current and new aggregation.

    Args:
        measure_name (str): The measure name
        current_agg (Aggregation): The current aggregation, from database
        new_agg (Aggregation): The new aggregation, computed from raw measures

    Raises:
        Exception: The measure name must be the same bewteen aggregations
        Exception: The dates must be different between aggregations

    Returns:
        Aggregation: The newly computed aggregation
    """

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


def aggregate_to_insert(m_definition: MeasureDefinition, agg: Aggregation):
    if type(agg) is not dict:
        agg = agg._mapping

    new_agg = Aggregation(
        measure_name=m_definition.name,
        start_date=agg["start_date"],
        created_by=agg["created_by"],
        group1=agg["group1"],
        group2=agg["group2"],
        group3=agg["group3"],
        sum=agg["sum"],
        count=agg["count"],
        count_not_zero=agg["count_not_zero"],
        min=agg["min"],
        max=agg["max"],
        avg=agg["avg"],
        std=agg["std"],
    )
    if m_definition.with_quartiles is True:
        # Save quartiles only when explicitly declared
        new_agg.median = agg["median"]
        new_agg.first_quartile = agg["first_quartile"]
        new_agg.third_quartile = agg["third_quartile"]
    return new_agg


def aggregate_to_update(m_definition: MeasureDefinition, agg: Aggregation):
    aggregate = {
        "b_id": agg.id,  # "id" cannot be mapped by SQLAlchemy
        "sum": agg.sum,
        "count": agg.count,
        "count_not_zero": agg.count_not_zero,
        "min": agg.min,
        "max": agg.max,
        "avg": agg.avg,
        "std": agg.std,
        "last_updated": datetime.now(),  # TODO: should be a trigger
    }
    if m_definition.with_quartiles:
        # Save quartiles only when explicitly declared
        aggregate["median"] = agg.median
        aggregate["first_quartile"] = agg.first_quartile
        aggregate["third_quartile"] = agg.third_quartile
    return aggregate


def build_aggregate_key(agg: Aggregation):
    """Build a dict key to retrieve aggregates

    After querying existing aggregates, we store them in a dict
    with a key used to retrieve them quickly, which is a concatenation
    of the search terms.

    Args:
        agg (Aggregation): The aggregate to build the key on

    Returns:
        str: The built key
    """
    date_key = agg.start_date.isoformat()
    created_by_key = agg.created_by or "null"
    group1_key = json.dumps(agg.group1)
    group2_key = json.dumps(agg.group2)
    group3_key = json.dumps(agg.group3)
    key = (
        date_key
        + "_"
        + created_by_key
        + "_"
        + group1_key
        + "_"
        + group2_key
        + "_"
        + group3_key
    )
    return key


def find_existing_aggregate(
    existing_aggregates: List[Aggregation], new_agg: Aggregation
):
    key = build_aggregate_key(new_agg)
    if key in existing_aggregates:
        return existing_aggregates[key]
    return None


def get_column_filter(grouped_measures: List[Aggregation], column: Any):
    """Get the filter to apply to the given Aggregation column

    Args:
        grouped_measures (List[Aggregation]): The aggregated raw measures
        column (Any): An Aggregation column

    Returns:
        Filter: The filter to apply on this column
    """
    column_name = column.name
    values = np.unique(
        [
            json.dumps(gm[column_name])
            if type(gm[column_name]) is dict
            else gm[column_name]
            for gm in grouped_measures
            if gm[column_name] is not None
        ]
    ).tolist()

    if len(values) == 0:
        return column.is_(None)
    else:
        return column.in_(values)


def query_existing_aggregates(
    measure_name: str, grouped_measures: List[Aggregation]
):
    """Query the existing aggregates based on aggregated raw measures.

    Args:
        measure_name (str): The measure name
        grouped_measures (List[Aggregation]): The list of aggregated measures

    Returns:
        dict: A dict of existing aggregates
    """
    filters = [
        Aggregation.measure_name == measure_name,
    ]
    filters.append(get_column_filter(grouped_measures, Aggregation.start_date))
    filters.append(get_column_filter(grouped_measures, Aggregation.created_by))
    filters.append(get_column_filter(grouped_measures, Aggregation.group1))
    filters.append(get_column_filter(grouped_measures, Aggregation.group2))
    filters.append(get_column_filter(grouped_measures, Aggregation.group3))

    aggs = db.session.query(Aggregation).filter(*filters).all()
    existing_aggregates = {}
    for agg in aggs:
        key = build_aggregate_key(agg)
        existing_aggregates[key] = agg
    return existing_aggregates


def backup_rejected_raw_measures(
    m_definition: MeasureDefinition, agg: Aggregation, end_date: str
):
    """Backup raw measures that cannot be aggregated.

    When raw measures are purged, quartiles cannot be computed anymore.
    We block this aggregation and backup the involved raw measures
    in the RefusedRawMeasures table.

    Args:
        m_definition (MeasureDefinition): The measure definition
        agg (Aggregation): The computed aggregate
        end_date (str): The end date to query raw measures
    """
    m_filter = get_filters_quartiles(m_definition, agg, end_date)
    measures = db.session.query(RawMeasure).filter(*m_filter).all()
    for m in measures:
        RefusedRawMeasure.insert_from_raw_measure(m)

    logging.error(
        "Prevent aggregate quartiles on purged measures {} - {}".format(
            m_definition.name, agg.start_date
        )
    )


def aggregate_raw_measures(m_definition: MeasureDefinition, force=False):
    """Aggregate raw measures on a time period and save them in the
    Aggregation table.

    Args:
        m_definition (MeasureDefinition): The measure definition

    Raises:
        Exception: Any exception raised during the process.

    Returns:
        (list(Aggregation), str): The aggregated tuples and the last saved
        aggregated date
    """
    try:
        start_date, end_date = find_dates_bounds(m_definition)
        if end_date is None:
            # No measures to aggregate
            logging.info("No new measure for {}".format(m_definition.name))
            return (None, None)
        if not force and not validate.is_execution_frequency_respected(
            start_date, m_definition
        ):
            # This execution is too close from the last run
            logging.info(
                "Execution is too close from the last run for: {}".format(
                    m_definition.name
                )
            )
            return (None, None)

        start_time = time.time()

        measure_name = m_definition.name
        grouped_measures = compute_all_aggregates_from_raw_measures(
            m_definition, start_date, end_date
        )
        existing_aggregates = []
        if len(grouped_measures) > 0:
            existing_aggregates = query_existing_aggregates(
                measure_name, grouped_measures
            )

        all_aggregates = []
        aggs_to_insert = []
        aggs_to_update = []
        for gm in grouped_measures:
            existing_agg = find_existing_aggregate(existing_aggregates, gm)

            if existing_agg is None:
                # This will be an insert in the Aggregation table
                agg = aggregate_to_insert(m_definition, gm)
                aggs_to_insert.append(agg)
                all_aggregates.append(agg)
            else:
                # This will be an update in the Aggregation table
                agg = compute_partial_aggregates(
                    measure_name, existing_agg, gm
                )
                if m_definition.with_quartiles:
                    if existing_agg.last_raw_measures_purged:
                        # Measures with quartiles should not be aggregated
                        # after a purge, since raw values are deleted.
                        backup_rejected_raw_measures(
                            m_definition, agg, end_date
                        )
                        continue

                    # We cannot compute partial aggregates for quartiles,
                    # thus all raw measures must be queried.
                    # Additional check might be necessary to deal with purge
                    quartiles = compute_quartiles_from_raw_measures(
                        m_definition, existing_agg, end_date
                    )
                    if quartiles is None:
                        raise Exception(
                            "No quartile computed for {}"
                            "on start_date {}".format(measure_name, start_date)
                        )
                    agg.median = quartiles.median
                    agg.first_quartile = quartiles.first_quartile
                    agg.third_quartile = quartiles.third_quartile
                    all_aggregates.append(agg)

                aggs_to_update.append(aggregate_to_update(m_definition, agg))

        if len(aggs_to_insert) > 0:
            # Insert all new aggregates
            db.session.add_all(aggs_to_insert)

        if len(aggs_to_update) > 0:
            # Update all the existing aggregates
            stmt = update(Aggregation).where(
                Aggregation.id == bindparam("b_id")
            )
            db.session.execute(stmt, aggs_to_update)

        agg_date = get_new_aggregation_date(m_definition, end_date)

        if agg_date is None:
            raise Exception(
                "No new aggregation date for measure {}".format(measure_name)
            )
        db.session.add(agg_date)
        db.session.commit()

        logging.debug(
            "--- %s seconds to update aggregate---"
            % (time.time() - start_time)
        )
        return all_aggregates, agg_date.last_aggregated_measure_date

    except Exception as err:
        print("Error while aggregating: " + repr(err))


def generate_wildcard_json(group_key):
    return {group_key: "*"}


def compute_wildcard_aggregate(
    m_definition: MeasureDefinition,
    wildcard_groups: List[str],
    from_date: datetime,
    to_date: datetime,
):
    """Compute wildcard aggregates for the given groups

    A wildcard aggregate is useful to exclude a group in the groupby aggregate.
    For instance, consider a measure definition with group1_key: 'slug':
    a wildcard on group1 will aggregate together all the measures with any
    slug value.


    Args:
        m_definition (MeasureDefinition): The measure definition
        wildcard_groups (List[str]): The list of groups to wildcard
        from_date (datetime): The starting date to query measures
        to_date (datetime): The ending date to query measures

    Returns:
        list(Aggregation): The inserted wildcard aggregates
    """

    # TODO: groups might be dynamics in the future
    not_wildcard_groups = ["group1", "group2", "group3"]
    for group in wildcard_groups:
        not_wildcard_groups.remove(group)

    query_args = [
        RawMeasure.created_by,
        RawMeasure.start_date,
    ]
    groupby_args = [RawMeasure.created_by, RawMeasure.start_date]

    # TODO: could be improved by mapping column name
    for group in not_wildcard_groups:
        if group == "group1":
            query_args.append(RawMeasure.group1)
            groupby_args.append(RawMeasure.group1)
        if group == "group2":
            query_args.append(RawMeasure.group2)
            groupby_args.append(RawMeasure.group2)
        if group == "group3":
            query_args.append(RawMeasure.group3)
            groupby_args.append(RawMeasure.group3)

    query_args += get_distributive_funcs_aggregation_query()
    query_args += get_algebraic_funcs_aggregation_query()
    if m_definition.with_quartiles is True:
        query_args += get_quartiles_funcs_aggregation_query()

    filters_args = get_filters_all_aggregations(
        m_definition, from_date, to_date
    )

    aggs = (
        db.session.query(*query_args)
        .filter(*filters_args)
        .group_by(*groupby_args)
        .all()
    )

    inserted_aggs = []
    for agg in aggs:
        measure = tuple_as_dict(agg)

        # TODO: groups might be dynamics in the future
        measure["group1"] = (
            generate_wildcard_json(m_definition.group1_key)
            if "group1" in wildcard_groups
            else agg.group1
        )
        measure["group2"] = (
            generate_wildcard_json(m_definition.group2_key)
            if "group2" in wildcard_groups
            else agg.group2
        )
        measure["group3"] = (
            generate_wildcard_json(m_definition.group3_key)
            if "group3" in wildcard_groups
            else agg.group3
        )
        existing_agg = Aggregation.query_aggregate_by_measure(
            m_definition.name, measure
        )
        if existing_agg is not None:
            db.session.delete(existing_agg)

        agg_to_insert = aggregate_to_insert(m_definition, measure)
        db.session.add(agg_to_insert)
        inserted_aggs.append(agg_to_insert)
    db.session.commit()

    return inserted_aggs
