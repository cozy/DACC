import random
import click
from urllib.parse import urljoin
import requests

# This scripts sends random measures to a DACC server on the dummy
# example-file-size-by-slug-monthly measure.
# The number of simulated instances can be specified.

AVAILABLE_SLUGS = [
    "drive",
    "payfit",
    "ameli",
    "maif",
    "maif-vie",
]


MONTHS = ["2021-12-01", "2022-01-01", "2022-02-01"]
MEASURE_NAME = "example-file-size-by-slug-monthly"

EXCLUDED_SLUG = "maif"
NON_EXCLUDED_LABEL = "sum-not-maif"


def pickRandomSlug():
    n_slugs = random.randint(1, len(AVAILABLE_SLUGS))
    return random.sample(AVAILABLE_SLUGS, k=n_slugs)


def computeSizeBySlug(instSlugs, prevMonth):
    sizeBySlug = {}
    for slug in instSlugs:
        size = 0
        if slug == "drive":
            size = round(random.uniform(0.1, 50.0), 3)
        else:
            size = round(random.uniform(0.01, 1.0), 3)
        if prevMonth:
            sizeBySlug[slug] = round(size + prevMonth[slug], 3)
        else:
            sizeBySlug[slug] = size
    return sizeBySlug


def aggregateNotExcluded(sizes):
    for m in range(len(MONTHS)):
        totalSize = 0
        for slug in sizes[m].keys():
            if EXCLUDED_SLUG not in slug:
                totalSize += sizes[m][slug]
        if totalSize != 0:
            sizes[m][NON_EXCLUDED_LABEL] = totalSize
    return sizes


def sendMeasures(dacc_address, token, sizes):
    url = urljoin(dacc_address, "/measure")
    if token:
        headers = {}
        headers["Authorization"] = "Bearer " + token

    for m in range(len(MONTHS)):
        for slug in sizes[m].keys():
            measure = {
                "createdBy": "drive",
                "measureName": MEASURE_NAME,
                "startDate": MONTHS[m],
                "group1": {"slug": slug},
                "value": sizes[m][slug],
            }
            r = requests.post(url, json=measure, headers=headers)
            if r.status_code == 201:
                print("measure sent: {}".format(measure))
            if r.status_code != 201:
                r.raise_for_status()
                print(r.text)


@click.command()
@click.argument("dacc_address")
@click.option("-n", "--n_instances", default=1, show_default=True)
@click.option("-t", "--token")
def send_random_measures(dacc_address, n_instances, token):
    insts = []
    for i in range(n_instances):
        slugs = pickRandomSlug()
        insts.append({"slugs": slugs})

    sizesInsts = []

    for i in range(n_instances):
        sizesMonth = []
        for m in range(len(MONTHS)):
            prevMonth = None
            if m > 0:
                prevMonth = sizesMonth[m - 1]
            sizeBySlug = computeSizeBySlug(insts[i]["slugs"], prevMonth)
            sizesMonth.append(sizeBySlug)
        sizesInsts.append(sizesMonth)

    for i in range(n_instances):
        sizesInsts[i] = aggregateNotExcluded(sizesInsts[i])
        sendMeasures(dacc_address, token, sizesInsts[i])


if __name__ == "__main__":
    send_random_measures()
