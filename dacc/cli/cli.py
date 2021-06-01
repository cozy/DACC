import click
from dacc import dacc, db, aggregation
from dacc.fixtures import fixtures


@dacc.cli.command("reset-all-tables")
def reset_tables():
    """Reset all tables in database"""

    click.confirm(
        "This will remove ALL DATA in database. Are you sure?", abort=True
    )
    print("Reset all tables in database...")
    db.drop_all()
    db.create_all()
    print("Done.")


@dacc.cli.command("show-table")
@click.argument("table_name")
def show_table(table_name):
    """Show a table content"""

    result = db.session.execute("SELECT * FROM {};".format(table_name))
    print(result.fetchall())


@dacc.cli.command("insert-fixtures-definition")
def insert_fixtures_definition():
    """Insert fixtures in database"""

    fixtures.insert_measures_definition_from_file()
    db.session.commit()


@dacc.cli.command("insert-random-measures")
@click.option("-n", "n_measures", default=1, show_default=True)
@click.option("-d", "--days", default=1, show_default=True)
@click.option(
    "--starting-day", "starting_day", default="2021-05-01", show_default=True
)
def insert_fixtures(n_measures, days, starting_day):
    """Insert random measures in database"""

    fixtures.insert_random_raw_measures(n_measures, days, starting_day)


@dacc.cli.command("compute-aggregation")
@click.argument("measure_name")
def compute_aggregation(measure_name):
    """Compute aggregation for a measure"""

    aggregation.aggregate_raw_measures(measure_name)
