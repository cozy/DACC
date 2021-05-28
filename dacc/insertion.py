from dacc.models import RawMeasures, MeasuresDefinition
from dacc import db


def insert_raw_measure(measure):
    group1 = measure["groups"][0] if "groups" in measure else None
    group2 = (
        measure["groups"][1]
        if "groups" in measure and len(measure["groups"]) > 1
        else None
    )
    group3 = (
        measure["groups"][2]
        if "groups" in measure and len(measure["groups"]) > 2
        else None
    )

    m = RawMeasures(
        measure_name=measure.get("measureName"),
        value=measure.get("value"),
        start_date=measure.get("startDate"),
        aggregation_period=measure.get("aggregationPeriod"),
        created_by=measure.get("createdBy"),
        group1=group1,
        group2=group2,
        group3=group3,
        is_aggregated=False,
    )
    db.session.add(m)
    db.session.commit()
    return m


def insert_measure_definition(definition):
    d = MeasuresDefinition(
        name=definition.get("name"),
        created_by=definition.get("createdBy"),
        description=definition.get("description"),
        aggregation_period=definition.get("aggregationPeriod"),
        contribution_threshold=definition.get("contributionThreshold"),
        group1_key=definition.get("group1Key"),
        group2_key=definition.get("group2Key"),
        group3_key=definition.get("group3Key"),
    )
    db.session.add(d)
    db.session.commit()
    return d
