from dacc import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class RawMeasures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_name = db.Column(db.String(100))
    value = db.Column(db.Numeric(precision=12, scale=2), default=1)
    start_date = db.Column(db.TIMESTAMP)
    last_updated = db.Column(db.DateTime, default=func.now())
    aggregation_period = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    group1 = db.Column(JSONB(none_as_null=True))
    group2 = db.Column(JSONB(none_as_null=True))
    group3 = db.Column(JSONB(none_as_null=True))
    is_aggregated = db.Column(db.Boolean)

    # TODO: indexing on last_updated might be good
    def query_by_name(measure_name):
        return (
            db.session.query(
                RawMeasures.created_by,
                RawMeasures.start_date,
                RawMeasures.group1,
                RawMeasures.group2,
                RawMeasures.group3,
                RawMeasures.value,
            )
            .filter(RawMeasures.measure_name == measure_name)
            .order_by(RawMeasures.last_updated)
            .all()
        )

    def query_most_recent_date(measure_name, from_date):
        return (
            db.session.query(RawMeasures.last_updated)
            .filter(
                RawMeasures.measure_name == measure_name,
                RawMeasures.last_updated > from_date,
            )
            .order_by(RawMeasures.last_updated.desc())
            .first()
        )


class MeasuresDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    org = db.Column(db.String(50))
    created_by = db.Column(db.String(100))
    group1_key = db.Column(db.String(100))
    group2_key = db.Column(db.String(100))
    group3_key = db.Column(db.String(100))
    description = db.Column(db.String)
    aggregation_period = db.Column(db.String(50))
    contribution_threshold = db.Column(db.Integer)
    aggregation_dates = relationship(
        "AggregationDates", uselist=False, back_populates="measures_definition"
    )

    def query_by_name(name):
        return (
            db.session.query(MeasuresDefinition)
            .filter(MeasuresDefinition.name == name)
            .first()
        )

    def query_all_names():
        return db.session.query(MeasuresDefinition.name).all()


class AggregationDates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measures_definition_id = db.Column(
        db.Integer, db.ForeignKey("measures_definition.id")
    )
    last_aggregated_measure_date = db.Column(db.TIMESTAMP)
    measures_definition = relationship(
        "MeasuresDefinition", back_populates="aggregation_dates"
    )

    def query_by_name(measure_name):
        return (
            db.session.query(AggregationDates)
            .join(MeasuresDefinition.aggregation_dates)
            .filter(MeasuresDefinition.name == measure_name)
            .first()
        )


class Aggregation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_name = db.Column(db.String(100))
    start_date = db.Column(db.TIMESTAMP)
    last_updated = db.Column(db.DateTime, default=func.now())
    created_by = db.Column(db.String(100))
    group1 = db.Column(JSONB(none_as_null=True))
    group2 = db.Column(JSONB(none_as_null=True))
    group3 = db.Column(JSONB(none_as_null=True))
    sum = db.Column(db.Numeric(precision=12, scale=2))
    count = db.Column(db.Integer)
    count_not_zero = db.Column(db.Integer)
    min = db.Column(db.Numeric(precision=12, scale=2))
    max = db.Column(db.Numeric(precision=12, scale=2))
    avg = db.Column(db.Numeric(precision=12, scale=2))
    std = db.Column(db.Numeric(precision=12, scale=2))

    def query_aggregate_by_measure(measure_name, m):
        return (
            db.session.query(Aggregation)
            .filter(
                Aggregation.measure_name == measure_name,
                Aggregation.start_date == m.start_date,
                Aggregation.created_by == m.created_by,
                Aggregation.group1 == m.group1,
                Aggregation.group2 == m.group2,
                Aggregation.group3 == m.group3,
            )
            .first()
        )
