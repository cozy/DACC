from dacc import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.hybrid import hybrid_method
from datetime import timedelta


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org = db.Column(db.String(100))
    token = db.Column(db.String(200))

    @staticmethod
    def query_by_org(org):
        return db.session.query(Auth).filter(Auth.org == org).first()

    @staticmethod
    def query_by_token(token):
        return db.session.query(Auth).filter(Auth.token == token).first()


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
    @staticmethod
    def query_by_name(measure_name):
        return (
            db.session.query(
                RawMeasure.created_by,
                RawMeasure.last_updated,
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

    @staticmethod
    def query_most_recent_last_updated(measure_name, from_date):
        return (
            db.session.query(RawMeasure.last_updated)
            .filter(
                RawMeasure.measure_name == measure_name,
                RawMeasure.last_updated > from_date,
            )
            .order_by(RawMeasure.last_updated.desc())
            .first()
        )

    @hybrid_method
    def max_retention_date(self, max_days):
        return self.last_updated + timedelta(days=max_days)


class MeasureDefinition(db.Model):
    # TODO add integrity checks such as control on group order, exec freq
    # consistency w.r.t. agg period, ...
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
    aggregation_threshold = db.Column(db.Integer, server_default=text("5"))
    access_app = db.Column(db.Boolean, server_default=text("false"))
    access_public = db.Column(db.Boolean, server_default=text("false"))
    with_quartiles = db.Column(db.Boolean, server_default=text("false"))
    max_days_to_update_quartile = db.Column(
        db.Integer, server_default=text("100")
    )
    aggregation_date = relationship(
        "AggregationDate",
        uselist=False,
        back_populates="measure_definition",
        passive_deletes=True,
    )

    @staticmethod
    def query_by_name(name):
        return (
            db.session.query(MeasureDefinition)
            .filter(MeasureDefinition.name == name)
            .first()
        )

    @staticmethod
    def query_all_names():
        return db.session.query(MeasureDefinition.name).all()

    @staticmethod
    def query_threshold(name):
        return (
            db.session.query(MeasureDefinition.aggregation_threshold)
            .filter(MeasureDefinition.name == name)
            .scalar_subquery()
        )


class AggregationDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measure_definition_id = db.Column(
        db.Integer, db.ForeignKey("measure_definition.id", ondelete="CASCADE")
    )
    last_aggregated_measure_date = db.Column(db.TIMESTAMP)
    measure_definition = relationship(
        "MeasureDefinition", back_populates="aggregation_date"
    )

    @staticmethod
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
    last_raw_measures_purged = db.Column(db.TIMESTAMP)
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
    std = db.Column(db.Numeric(precision=12, scale=2), default=0)
    median = db.Column(db.Numeric(precision=12, scale=2))
    first_quartile = db.Column(db.Numeric(precision=12, scale=2))
    third_quartile = db.Column(db.Numeric(precision=12, scale=2))

    @staticmethod
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

    @staticmethod
    def query_aggregates_by_measure_name_from_date(measure_name, date):
        return (
            db.session.query(Aggregation)
            .filter(
                Aggregation.measure_name == measure_name,
                Aggregation.start_date >= date,
            )
            .all()
        )

    @staticmethod
    def query_range_with_threshold(
        measure_name, start_date, end_date, created_by=None
    ):
        filters = [
            Aggregation.measure_name == measure_name,
            Aggregation.start_date >= start_date,
            Aggregation.start_date < end_date,
        ]
        if created_by is not None:
            filters.append(Aggregation.created_by == created_by)

        subquery_threshold = MeasureDefinition.query_threshold(measure_name)
        filters.append(Aggregation.count >= subquery_threshold)
        return (
            db.session.query(Aggregation)
            .filter(*filters)
            .order_by(Aggregation.start_date)
            .all()
        )
