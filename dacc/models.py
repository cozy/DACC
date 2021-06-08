from dacc import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class RawMeasure(db.Model):
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

    # TODO: indexing on last_updated might be good
    def query_by_name(measure_name):
        return (
            db.session.query(
                RawMeasure.created_by,
                RawMeasure.start_date,
                RawMeasure.group1,
                RawMeasure.group2,
                RawMeasure.group3,
                RawMeasure.value,
            )
            .filter(RawMeasure.measure_name == measure_name)
            .order_by(RawMeasure.last_updated)
            .all()
        )

    def query_most_recent_date(measure_name, from_date):
        return (
            db.session.query(RawMeasure.last_updated)
            .filter(
                RawMeasure.measure_name == measure_name,
                RawMeasure.last_updated > from_date,
            )
            .order_by(RawMeasure.last_updated.desc())
            .first()
        )


class MeasureDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    org = db.Column(db.String(50))
    created_by = db.Column(db.String(100))
    group1_key = db.Column(db.String(100))
    group2_key = db.Column(db.String(100))
    group3_key = db.Column(db.String(100))
    description = db.Column(db.String)
    aggregation_period = db.Column(db.String(50))
    execution_frequency = db.Column(db.String(50))
    contribution_threshold = db.Column(db.Integer)
    access_app = db.Column(db.Boolean)
    access_public = db.Column(db.Boolean)
    aggregation_date = relationship(
        "AggregationDate", uselist=False, back_populates="measure_definition"
    )

    def query_by_name(name):
        return (
            db.session.query(MeasureDefinition)
            .filter(MeasureDefinition.name == name)
            .first()
        )

    def query_all_names():
        return db.session.query(MeasureDefinition.name).all()


class AggregationDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_definition_id = db.Column(
        db.Integer, db.ForeignKey("measure_definition.id")
    )
    last_aggregated_measure_date = db.Column(db.TIMESTAMP)
    measure_definition = relationship(
        "MeasureDefinition", back_populates="aggregation_date"
    )

    def query_by_name(measure_name):
        return (
            db.session.query(AggregationDate)
            .join(MeasureDefinition.aggregation_date)
            .filter(MeasureDefinition.name == measure_name)
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
