from dacc import db
from sqlalchemy.sql import text
from alembic_utils.pg_materialized_view import PGMaterializedView


class FilteredAggregation:
    name = "filtered_aggregation"
    definition = """
                SELECT id, measure_name, start_date, created_by,
                group1::text, group2::text, group3::text,
                sum, count, count_not_zero, min, max, avg, std,
                median, first_quartile, third_quartile,
                last_updated
                FROM aggregation as agg
                WHERE agg.count >=
                    (SELECT m.aggregation_threshold
                    FROM measure_definition as m
                    WHERE m.name = agg.measure_name)
            """

    @classmethod
    def get_pg_view(cls):

        return PGMaterializedView(
            schema="public",
            signature=cls.name,
            definition=cls.definition,
            with_data=True,
        )

    @classmethod
    def create(cls, name=None):
        if name is None:
            name = cls.name
        create_view_sql = "CREATE MATERIALIZED VIEW {} AS ({})".format(
            name, cls.definition
        )

        stmt = text(create_view_sql)
        db.session.execute(stmt)
        db.session.commit()

    @classmethod
    def udpate(cls):
        query_sql = "REFRESH MATERIALIZED VIEW {};".format(cls.name)
        stmt = text(query_sql)
        db.session.execute(stmt)
        db.session.commit()

    @classmethod
    def delete(cls, name=None):
        if name is None:
            name = cls.name
        query_sql = "DROP MATERIALIZED VIEW {};".format(cls.name)
        stmt = text(query_sql)
        db.session.execute(stmt)
        db.session.commit()

    @classmethod
    def recreate_view(cls):
        tmp_view_name = "tmp_{}".format(cls.name)
        print("Create new view...")
        FilteredAggregation.create(tmp_view_name)
        print("Delete old view...")
        FilteredAggregation.delete(cls.name)
        query_sql = "ALTER MATERIALIZED VIEW {} RENAME TO {};".format(
            tmp_view_name, cls.name
        )
        stmt = text(query_sql)
        db.session.execute(stmt)
        db.session.commit()
        print("Done!")
