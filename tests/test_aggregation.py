from dacc import db, aggregation
from dacc.models import RawMeasures
import pandas as pd
from sqlalchemy import distinct


def query_all_measures_name():
    results = db.session.query(distinct(RawMeasures.measure_name)).all()
    return [v for v, in results]


def convert_columns(df_raw):
    if 'group1' in df_raw:
        df_raw = df_raw.astype({'group1': 'str'})
    if 'group2' in df_raw:
        df_raw = df_raw.astype({'group2': 'str'})
    if 'group3' in df_raw:
        df_raw = df_raw.astype({'group3': 'str'})
    df_raw = df_raw.astype({'value': 'float'})
    return df_raw


def test_aggregations():
    measure_names = query_all_measures_name()
    for measure_name in measure_names:
        aggregated_rows = aggregation.query_measures_to_aggregate_by_name(
            measure_name, None, None)

        raw_measures = RawMeasures.query_by_name(measure_name)

        df_raw = pd.DataFrame(data=raw_measures, columns=[
                              "created_by", "start_date", "group1", "group2", "group3",  "value"])

        #  Remove null columns
        columns = (df_raw.columns[df_raw.notna().any()].tolist())
        df_raw = df_raw.dropna(axis='columns')

        df_raw = convert_columns(df_raw)
        columns.remove("value")  #  Remove value column to group by

        sums = df_raw.groupby(columns, as_index=False).sum()
        counts = df_raw.groupby(columns, as_index=False).count()
        mins = df_raw.groupby(columns, as_index=False).min()
        maxs = df_raw.groupby(columns, as_index=False).max()
        avgs = df_raw.groupby(columns, as_index=False).mean()

        assert len(aggregated_rows) == len(sums)
        for i, _ in enumerate(aggregated_rows):
            assert aggregated_rows[i].sum == sums.value[i]
            assert aggregated_rows[i].count == counts.value[i]
            assert aggregated_rows[i].min == mins.value[i]
            assert aggregated_rows[i].max == maxs.value[i]
            assert aggregated_rows[i].avg == avgs.value[i]


def test_aggregate_raw_measures():
    aggregation.aggregate_raw_measures('connection-count-daily')
