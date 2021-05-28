import pytest
import os

from dacc import dacc, db
from dacc.fixtures import fixtures


@pytest.fixture(scope="session", autouse=True)
def init():
    db.drop_all()
    db.create_all()

    fixtures.insert_raw_measures_from_file()
    fixtures.insert_measures_definition_from_file()
