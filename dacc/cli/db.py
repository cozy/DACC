import click
from dacc import dacc, db, aggregation
from dacc.fixtures import fixtures


@dacc.cli.command("reset-all-tables")
def reset_tables():
    """Reset all tables in database"""

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

    fixtures.insert_fixtures_measures_definition()


@dacc.cli.command("insert-random-measures")
@click.option("-n", default=1, show_default=True)
def insert_fixtures(n):
    """Insert random measures in database"""

    fixtures.insert_random_raw_measures(n_measures)
