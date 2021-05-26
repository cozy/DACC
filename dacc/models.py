from dacc import db
from sqlalchemy.dialects.postgresql import JSONB

class RawMeasures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_name = db.Column(db.String(100))
    value = db.Column(db.Numeric)
    start_date = db.Column(db.TIMESTAMP)
    production_date = db.Column(db.TIMESTAMP)
    aggregation_period = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    group1 = db.Column(JSONB)
    group2 = db.Column(JSONB)
    group3 = db.Column(JSONB)
    is_aggregated = db.Column(db.Boolean)

    def query_by_name(measure_name):
        return db.session \
            .query(
                RawMeasures.created_by,
                RawMeasures.start_date,
                RawMeasures.group1,
                RawMeasures.group2,
                RawMeasures.group3,
                RawMeasures.value) \
            .filter(RawMeasures.measure_name == measure_name) \
            .all()

class MeasuresDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    org = db.Column(db.String(550))
    created_by = db.Column(db.String(100))
    group1_key = db.Column(db.String(100))
    group2_key = db.Column(db.String(100))
    group3_key = db.Column(db.String(100))
    description = db.Column(db.String)
    aggregation_period = db.Column(db.String(50))
    contribution_threshold = db.Column(db.Integer)


class Aggregation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_name = db.Column(db.String(100))
    start_date = db.Column(db.TIMESTAMP)
    production_date = db.Column(db.TIMESTAMP)
    created_by = db.Column(db.String(100))
    group1 = db.Column(JSONB)
    group2 = db.Column(JSONB)
    group3 = db.Column(JSONB)
    sum = db.Column(db.Numeric)
    count = db.Column(db.Numeric)
    count_not_zero = db.Column(db.Numeric)
    min = db.Column(db.Numeric)
    max = db.Column(db.Numeric)
    average = db.Column(db.Numeric)
    std = db.Column(db.Numeric)