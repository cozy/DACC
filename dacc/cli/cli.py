import click
import sys
import os
import uuid
import json
from dacc import dacc, db, aggregation, consts, insertion
from tests.fixtures import fixtures
from dacc.models import (
    MeasureDefinition,
    Auth,
    Aggregation,
    AggregationDate,
)
from dacc.views import FilteredAggregation
import requests
from urllib.parse import urljoin
from tabulate import tabulate


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@dacc.cli.command("reset-all-tables")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="This will remove ALL DATA in database. Are you sure?",
)
def reset_tables():
    """Reset all tables in database"""

    try:
        print("Reset all tables in database...")

        db.drop_all()
        db.create_all()
        FilteredAggregation.create()
        print("Done.")
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.command("create-all-tables")
def create_tables():
    """Create all tables in database"""
    try:
        db.create_all()
        print("Done.")
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


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
        raise click.Abort()


@dacc.cli.command("show-table")
@click.argument("table_name")
def show_table(table_name):
    """Show a table content"""

    try:
        query_column_names = """
                                SELECT column_name
                                FROM information_schema.columns
                                WHERE table_name='{}';
                            """.format(
            table_name
        )
        column_names = db.session.execute(query_column_names).fetchall()
        column_names = [col[0] for col in column_names]
        query_table = "SELECT * FROM {};".format(table_name)
        table_content = db.session.execute(query_table).fetchall()
        print(tabulate(table_content, headers=column_names))
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.command("delete-aggregations-from-date")
@click.argument("measure_name")
@click.argument("start_date")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="This will remove aggregations in database, are you sure?",
)
def delete_aggregation(measure_name, start_date):
    """Delete all the aggregations computed for a measure, starting from
    the given date and set the last_aggregation_date to this date.
    WARNING: this should be used care, as manually setting
    last_aggregation_date might have side-effect if new measures with old
    start_date are implied.
    """
    try:
        aggs = Aggregation.query_aggregates_by_measure_name_from_date(
            measure_name, start_date
        )
        for agg in aggs:
            db.session.delete(agg)

        m_def_id = MeasureDefinition.query_by_name(measure_name).id
        db.session.query(AggregationDate).filter(
            AggregationDate.measure_definition_id == m_def_id
        ).update({"last_aggregated_measure_date": start_date})
        print("{} deleted aggregates".format(len(aggs)))
        print(
            "AggregationDate for {} (id {}) updated to date: {}".format(
                measure_name, m_def_id, start_date
            )
        )
        db.session.commit()

    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.command("insert-definitions-json")
@click.option(
    "-f", "file_path", default="assets/definitions.json", show_default=True
)
def insert_measure_definition_json(file_path):
    """Insert measure definitions from file"""
    try:
        path = os.path.join(consts.ROOT_PATH, file_path)
        f = open(path, "r")
        data = json.load(f)
        definitions = data["definitions"]
        for m_def in definitions:
            db_def = MeasureDefinition.query.get(m_def.get("id"))
            if db_def:
                db_def.name = m_def.get("name")
                db_def.org = (m_def.get("org"),)
                db_def.created_by = m_def.get("createdBy")
                db_def.group1_key = m_def.get("group1Key")
                db_def.group2_key = m_def.get("group2Key")
                db_def.group3_key = m_def.get("group3Key")
                db_def.description = m_def.get("description")
                db_def.aggregation_period = m_def.get("aggregationPeriod")
                db_def.execution_frequency = m_def.get("executionFrequency")
                db_def.aggregation_threshold = m_def.get(
                    "aggregationThreshold"
                )
                db_def.access_app = m_def.get("accessApp")
                db_def.access_public = m_def.get("accessPublic")
                db_def.with_quartiles = m_def.get("withQuartiles")
            else:
                insertion.insert_measure_definition(m_def)
                print("New definition inserted: {}".format(m_def.get("name")))

        db.session.commit()
        print("Done.")
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


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


@dacc.cli.command("send-random-measures")
@click.argument("dacc_address")
@click.option("-n", "n_measures", default=1, show_default=True)
@click.option("-d", "--days", default=1, show_default=True)
@click.option(
    "--starting-day", "starting_day", default="2021-05-01", show_default=True
)
@click.option("-m", "--measure_name")
@click.option("-t", "--token")
def send_random_measures(
    dacc_address, n_measures, days, starting_day, measure_name, token
):
    """Send random measures to a dacc server"""

    measures = fixtures.generate_random_raw_measures(
        n_measures, days, starting_day, measure_name
    )

    for i, measure in enumerate(measures):
        url = urljoin(dacc_address, "/measure")
        if token:
            headers = {}
            headers["Authorization"] = "Bearer " + token
        r = requests.post(url, json=measure, headers=headers)
        if r.status_code == 201:
            print("measure {} sent: {}".format((i + 1), measure))
        if r.status_code != 201:
            r.raise_for_status()
            print(r.text)
    print("All measures sent!")


@dacc.cli.command("compute-aggregation")
@click.argument("measure_name")
@click.option(
    "-f",
    "--force",
    is_flag=True,
)
def compute_aggregation(measure_name, force):
    """Compute aggregation for a measure"""

    try:
        m_def = MeasureDefinition.query_by_name(measure_name)
        if m_def is None:
            print("No measure definition found for: {}".format(measure_name))
            sys.exit()
        agg, date = aggregation.aggregate_raw_measures(m_def, force=force)
        if agg is None:
            print("No aggregation were made for: {}".format(measure_name))
        else:
            print("{} aggregations saved until: {}".format(len(agg), date))
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.command("compute-all-aggregations")
@click.option(
    "-f",
    "--force",
    is_flag=True,
)
def compute_all_aggregations(force):
    """Compute aggregation for all measures"""

    try:
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
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.command("create-filtered-aggregation-view")
def create_filtered_aggregation_view():
    """Create the filtered aggregation view"""
    try:
        FilteredAggregation.create()
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.command("update-filtered-aggregation-view")
def refresh_filtered_aggregation_view():
    """Refresh the filtered aggregation view"""
    try:
        FilteredAggregation.udpate()
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@dacc.cli.group()
def token():
    """Token management commands."""
    pass


@token.command("create")
@click.argument("org")
def create_token(org):
    """Create an authentication token for an org"""
    try:
        token = uuid.uuid4()
        auth = Auth(org=org, token=token)
        db.session.add(auth)
        db.session.commit()
        print("Token created for {}: {}".format(org, token))
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@token.command("get")
@click.argument("org")
def get_token(org):
    """Get an authentication token for an org"""
    try:
        auth = Auth.query_by_org(org)
        print(auth.token)
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@token.command("update")
@click.argument("org")
def update_token(org):
    """Update an authentication token for an org"""
    try:
        auth = Auth.query_by_org(org)
        auth.token = uuid.uuid4()
        db.session.commit()
        print("Token updated for {}: {}".format(org, auth.token))
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()


@token.command("delete-org")
@click.argument("org")
def delete_org(org):
    """Delete an org with its associated token"""
    try:
        auth = Auth.query_by_org(org)
        db.session.delete(auth)
        db.session.commit()
    except Exception as err:
        print("Command failed: {}".format(repr(err)))
        raise click.Abort()
