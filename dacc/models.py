from dacc import db


class RawMeasures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_name = db.Column(db.String(100))
    value = db.Column(db.Numeric)
    start_date = db.Column(db.TIMESTAMP)
    aggregation_period = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    group1 = db.Column(db.JSON)
    group2 = db.Column(db.JSON)
    group3 = db.Column(db.JSON)
    is_aggregated = db.Column(db.Boolean)


class MeasuresDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    created_by = db.Column(db.String(100))
    group1_key = db.Column(db.String(100))
    group2_key = db.Column(db.String(100))
    group3_key = db.Column(db.String(100))
    description = db.Column(db.String)
    aggregation_period = db.Column(db.String(50))
    contribution_threshold = db.Column(db.Integer)
