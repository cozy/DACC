import json
import random
import os
from sqlalchemy.sql import text
from dacc import models, db
from dacc import insertion

APPS = ["ecolyo", "drive", "banks", "pass"]


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


def insert_random_raw_measures(n_measures):
    try:
        defs = models.MeasuresDefinition.query.all()
        for i in range(n_measures):
            random_def = random.choice(defs)
            group1, group2, group3 = generate_groups(random_def)
            measure = {
                "measureName": random_def.name,
                "value": random.randint(0, 100),
                "startDate": "2020-05-01",
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


def insert_from_fixture(file_name):
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
    insert_from_fixture("raw_measures.sql")


def insert_measures_definition_from_file():
    insert_from_fixture("measures_definition.sql")
