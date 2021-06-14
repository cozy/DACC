import click
import sys
import os
from dacc import dacc, db, aggregation, consts
from tests.fixtures import fixtures
from dacc.models import MeasureDefinition, FilteredAggregation
from sqlalchemy import exc


@dacc.cli.command("reset-all-tables")
def reset_tables():
    """Reset all tables in database"""

    try:
        click.confirm(
            "This will remove ALL DATA in database. Are you sure?", abort=True
        )
        print("Reset all tables in database...")

        db.drop_all()
        db.create_all()
        FilteredAggregation.create()
        print("Done.")
    except Exception as err:
        print("Command failed: {}".format(repr(err)))


@dacc.cli.command("reset-table")
@click.argument("table_name")
def reset_table(table_name):
    """Reset a table in database"""

    try:
        click.confirm(
            "This will remove ALL DATA in the table. Are you sure?", abort=True
        )
        print("Reset all tuples in table...")
        db.session.execute("DELETE FROM {};".format(table_name))
        db.session.commit()
        print("Done.")
    except Exception as err:
        print("Command failed: {}".format(repr(err)))


@dacc.cli.command("show-table")
@click.argument("table_name")
def show_table(table_name):
    """Show a table content"""

    try:
        result = db.session.execute("SELECT * FROM {};".format(table_name))
        print(result.fetchall())
    except Exception as err:
        print("Command failed: {}".format(repr(err)))


@dacc.cli.command("insert-definitions")
@click.option(
    "-f", "file_path", default="data/definitions.sql", show_default=True
)
def insert_measure_definition(file_path):
    """Insert measure definitions from file"""

    try:
        path = os.path.join(consts.ROOT_PATH, file_path)
        f = open(path, "r")
        lines = f.readlines()
        for stmt in lines:
            print(stmt)
            try:
                db.session.execute(stmt)
            except exc.IntegrityError:
                db.session.rollback()
                print("IGNORED - Already exist.")
                pass
        db.session.commit()
    except Exception as err:
        print("Command failed: {}".format(repr(err)))


@dacc.cli.command("insert-fixtures-from-file")
@click.argument("fixture_type")
def insert_fixtures_definition(fixture_type):
    """Insert fixture file in database"""

    if fixture_type == "raw":
        fixtures.insert_raw_measures_from_file()
    elif fixture_type == "definition":
        fixtures.insert_measures_definition_from_file()
    elif fixture_type == "dates":
        fixtures.insert_aggregation_dates_from_file()
    db.session.commit()


@dacc.cli.command("insert-random-measures")
@click.option("-n", "n_measures", default=1, show_default=True)
@click.option("-d", "--days", default=1, show_default=True)
@click.option(
    "--starting-day", "starting_day", default="2021-05-01", show_default=True
)
@click.option("-m", "--measure_name")
def insert_fixtures(n_measures, days, starting_day, measure_name):
    """Insert random measures in database"""

    fixtures.insert_random_raw_measures(
        n_measures, days, starting_day, measure_name
    )


@dacc.cli.command("compute-aggregation")
@click.argument("measure_name")
@click.option("-f", "--force", default=False, show_default=True, type=bool)
def compute_aggregation(measure_name, force):
    """Compute aggregation for a measure"""

    m_def = MeasureDefinition.query_by_name(measure_name)
    if m_def is None:
        print("No measure definition found for: {}".format(measure_name))
        sys.exit()
    agg, date = aggregation.aggregate_raw_measures(m_def, force=force)
    if agg is None:
        print("No aggregation were made for: {}".format(measure_name))
    else:
        print("{} aggregations saved until: {}".format(len(agg), date))


@dacc.cli.command("compute-all-aggregations")
@click.option("-f", "--force", default=False, show_default=True, type=bool)
def compute_all_aggregations(force):
    """Compute aggregation for all measures"""

    m_defs = db.session.query(MeasureDefinition).all()
    for m_def in m_defs:
        agg, date = aggregation.aggregate_raw_measures(m_def, force=force)
        if agg is None:
            print("No aggregation were made for: {}".format(m_def.name))
        else:
            print(
                "{} aggregations saved until {} for: {}".format(
                    len(agg), date, m_def.name
                )
            )


@dacc.cli.command("create-filtered-aggregation-view")
def create_filtered_aggregation_view():
    try:
        FilteredAggregation.create()
    except Exception as err:
        print("Command failed: {}".format(repr(err)))


@dacc.cli.command("update-filtered-aggregation-view")
def refresh_filtered_aggregation_view():
    try:
        FilteredAggregation.udpate()
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
