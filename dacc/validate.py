from dacc.models import MeasureDefinition
from dacc import utils
from dateutil.parser import parse
from datetime import datetime


def check_incoming_raw_measure(measure):
    """Check the incoming raw measure is valid.

    Args:
        measure (dict): The raw measure

    Raises:
        Exception: The measure name is not given
        Exception: The measure name does not exist
        Exception: The value is not given
        Exception: The value type is not correct
        Exception: The startDate is not given
        Exception: The startDate is not correct
        Exception: The groups format is not correct
        Exception: The groups key does not match measure definition

    Returns:
        bool: True if the measure is valid
    """

    if measure is None:
        raise Exception("The measure cannot be empty")

    if "measureName" not in measure:
        raise Exception("A measure name must be given")

    m_def = MeasureDefinition.query_by_name(measure["measureName"])
    if m_def is None:
        raise Exception(
            "No measure definition found for: {}".format(
                measure["measureName"]
            )
        )

    if "value" not in measure:
        raise Exception("A value must be given")
    try:
        float(measure["value"])
    except ValueError:
        raise Exception("value type is incorrect, it must be a number")

    if "startDate" not in measure:
        raise Exception("A start date must be given")
    try:
        parse(measure["startDate"])
    except ValueError:
        raise Exception("startDate type is incorrect, it must be a date")

    if "groups" in measure and len(measure["groups"]) > 0:
        group1_key = None
        group2_key = None
        group3_key = None
        try:
            group1 = measure["groups"][0]
            group1_key = list(group1.keys())[0]
            if len(measure["groups"]) > 1:
                group2 = measure["groups"][1]
                group2_key = list(group2.keys())[0]
            if len(measure["groups"]) > 2:
                group3 = measure["groups"][2]
                group3_key = list(group3.keys())[0]
        except Exception:
            raise Exception("groups format is incorrect")

        if m_def.group1_key != group1_key:
            raise Exception(
                "Group key does not match measure definition: {}".format(
                    group1_key
                )
            )
        if m_def.group2_key != group2_key:
            raise Exception(
                "Group key does not match measure definition: {}".format(
                    group2_key
                )
            )
        if m_def.group3_key != group3_key:
            raise Exception(
                "Group key does not match measure definition: {}".format(
                    group3_key
                )
            )
    return True


def is_execution_frequency_respected(
    start_date: datetime, m_definition: MeasureDefinition
):
    """Check if the the given measure can be executed w.r.t
    to the execution frequency and the date interval between a
    start date and now.

    Args:
        start_date (datetime): The last execution date
        m_definition (MeasureDefinition): The measure definition

    Returns:
        bool: True if the execution frequency is respected
    """
    end_date = datetime.now()
    return utils.is_dates_interval_higher(
        start_date, end_date, m_definition.execution_frequency
    )
