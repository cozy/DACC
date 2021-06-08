import random
import os
from dateutil.parser import parse
from datetime import timedelta
from sqlalchemy.sql import text
from dacc import models, db
from dacc import insertion

APPS = ["ecolyo"]


def generate_groups(measure_definition):
    group1 = None
    group2 = None
    group3 = None
    if measure_definition.name == "connection-count-daily":
        group1_val = random.choice(["mobile", "desktop"])
        group1 = {"device": group1_val}
    elif measure_definition.name == "konnector-event-daily":
        group1_val = random.choice(["grdf", "edf", "egl"])
        group2_val = random.choice(["connexion", "refresh"])
        group3_val = random.choice(["success", "error"])

        group1 = {"slug": group1_val}
        group2 = {"event_type": group2_val}
        group3 = {"status": group3_val}

    elif measure_definition.name == "energy-consumption-daily":
        group1_val = random.choice(["electricity", "water", "gas"])
        group1 = {"energy_type": group1_val}

    return (group1, group2, group3)


def insert_random_raw_measures(n_measures, n_days, starting_day):
    try:
        starting_day = parse(starting_day)
        days = [starting_day + timedelta(days=i) for i in range(n_days)]
        defs = models.MeasureDefinition.query.all()
        if not defs:
            print("Please insert measures definition first.")
            return

        for i in range(n_measures):
            random_def = random.choice(defs)
            group1, group2, group3 = generate_groups(random_def)
            measure = {
                "measureName": random_def.name,
                "value": random.randint(0, 100),
                "startDate": random.choice(days),
                "createdByApp": random.choice(APPS),
                "groups": [],
            }
            if group1:
                measure["groups"].append(group1)
            if group2:
                measure["groups"].append(group2)
            if group3:
                measure["groups"].append(group3)

            insertion.insert_raw_measure(measure)
            print("Raw measure inserted : {}".format(measure))
    except Exception as e:
        print("Exception during fixture insertion: " + repr(e))


def insert_from_fixture_file(file_name):
    try:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(file_path, "r") as f:
            query = text(f.read())
            print("Insert from fixture...")
            print(query)
            db.session.execute(query)
    except Exception as e:
        print("Exception during fixture insertion: " + repr(e))


def insert_raw_measures_from_file():
    insert_from_fixture_file("raw_measures.sql")


def insert_measures_definition_from_file():
    insert_from_fixture_file("measures_definition.sql")


def insert_aggregation_dates_from_file():
    insert_from_fixture_file("aggregation_dates.sql")
