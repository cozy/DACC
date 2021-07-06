from dacc.models import RawMeasure, MeasureDefinition
from dacc import db


def insert_raw_measure(measure):
    """Insert JSON raw measure in database

    Args:
        measure (JSON): The JSON-formatted raw measure

    Returns:
        RawMeasure: The inserted raw measure in database
    """
    try:
        m = RawMeasure(
            measure_name=measure.get("measureName"),
            value=measure.get("value"),
            start_date=measure.get("startDate"),
            aggregation_period=measure.get("aggregationPeriod"),
            created_by=measure.get("createdBy"),
            group1=measure.get("group1"),
            group2=measure.get("group2"),
            group3=measure.get("group3"),
        )
        db.session.add(m)
        db.session.commit()
        return m
    except Exception as err:
        print("Error on measure insertion: " + repr(err))


def insert_measure_definition(definition):
    """Insert JSON measure definition in database

    Args:
        definition (JSON): The JSON-formatted definition

    Returns:
        MeasureDefinition: The inserted definition in database
    """
    try:
        d = MeasureDefinition(
            id=definition.get("id"),
            name=definition.get("name"),
            org=definition.get("org"),
            created_by=definition.get("createdBy"),
            group1_key=definition.get("group1Key"),
            group2_key=definition.get("group2Key"),
            group3_key=definition.get("group3Key"),
            description=definition.get("description"),
            aggregation_period=definition.get("aggregationPeriod"),
            execution_frequency=definition.get("executionFrequency"),
            aggregation_threshold=definition.get("aggregationThreshold"),
            access_app=definition.get("accessApp"),
            access_public=definition.get("accessPublic"),
        )
        db.session.add(d)
        db.session.commit()
        return d
    except Exception as err:
        print("Error on measure insertion: " + repr(err))
