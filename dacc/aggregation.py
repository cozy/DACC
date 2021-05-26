from dacc.models import RawMeasures
from dacc import db
from sqlalchemy import func

def query_measures_to_aggregate_by_name(measure_name):
    return db.session \
        .query(RawMeasures.created_by, RawMeasures.start_date, func.sum(RawMeasures.value).label('sum')) \
        .filter(RawMeasures.measure_name == measure_name) \
        .group_by(RawMeasures.created_by, RawMeasures.start_date, RawMeasures.group1)


# TODO: this should insert in aggregation table
def aggregate_raw_measures(measure_name):
    try:
        measures = query_measures_to_aggregate(measure_name)
        for m in measures:
            print('measure : {}'.format(m))
    except Exception as err:
        print("Error while aggregating: " + repr(err))

    
