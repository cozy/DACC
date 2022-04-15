# DACC

The Data Aggregator Cross Cozy (DACC)
# Setup


## Install

To setup the environement and install dependencies, simply run:

```
./mkenv.sh
```

## Config

Copy the template into a new config file:

```
cp config-template.yml config.yml
```

Then, edit `config.yml` to suit your needs.


## Run

```
source venv/bin/activate
flask run
```

# API
## Add a measure

You can request the `/measure` endpoint to add a raw measure:

```
$ curl -X POST -H 'Authorization: Bearer <token>' -H 'Content-Type: application/json' http://localhost:5000/measure -d @measure.json
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 12
Server: Werkzeug/2.0.1 Python/3.8.10

{
  "ok": "true"
}

```

ℹ️ If you want to request an actual server, replace `http://localhost:5000/measure` by your DACC URL. For example, `https://dacc.cozycloud.cc/measure`, or `https://dacc-dev.cozycloud.cc/measure` for tests.


ℹ️ The `token` is automatically injected by the stack when using a remote-doctype. Here is the [remote-doctype](https://github.com/cozy/cozy-doctypes/tree/master/cc.cozycloud.dacc) that must be used to request the Cozy's DACC server. You can also use the one [for developement](https://github.com/cozy/cozy-doctypes/tree/master/cc.cozycloud.dacc-dev).
To know how to use a remote-doctype from a Cozy app, see the [stack documentation](https://docs.cozy.io/en/cozy-stack/remote/).

### Measure format

Here is an example of a valid measure:
```
{
  "measureName": "konnector-event-daily",
  "value": 1,
  "startDate": "2022-01-01",
  "createdBy": "ecolyo",
  "group1": {
      "slug": "enedis"
  },
  "group2": {
      "event_type": "connection"
  },
  "group3": {
      "status": "success"
  }
}
```

The expected fields are the following:
* `measureName`: {string} the name of the measure. It must match an existing measure name on the DACC server.
* `value`: {number} the measured value. It can be 0 but never `null`.
* `startDate`: {date} the starting date of the measure. The expected date format is `ISO 8601`. It must be set in relation with the `aggregationPeriod` for this measure: for example, if the `aggregationPeriod` is `day`, then `start_date` must represent the measured day, e.g. `2022-01-01`.
* `createdBy`: {string} the application that produced the measure.
* `group1`: {object} The first group. Groups are used to combinate measures depending on attributes specified in the measure definition. Each group is a key-value entry, where the key is set in the measure definition. Here, the key must match the `group1_key` of the associated measure definition.
* `group2`: {object} The second group. Its key must match the `group2_key` of the associated measure definition.
* `group3`: {object} The third group. Its key must match the `group3_key` of the associated measure definition.


## Measure definition

A measure is defined by the following fields:
* `name`: {string} the name of the measure. It must indicate what is measured and should include the aggregation period, if relevant, e.g. "connexion-daily", "konnector-error-monthly", etc.
* `org`: {string} the organization defining this measure.
* `group1_key`: {string} the first grouping key.
* `group2_key`: {string} the second grouping key.
* `group3_key`: {string} the third grouping key.
* `description`: {string} a human-readable description of the measure.
* `aggregation_period`: {string} the period on which is computed the raw measure on the app side. It can be `day`, `week`, `month`.
* `execution_frequency`: {string} the frequency on which the measure should be computed on the DACC. It can be `day`, `week`, `month`.
* `aggregation_threshold`: {number} the minimal threshold contribution above which one can access an aggregated result. This threshold must be a trade-off between security (too low would put user privacy at risk) and usability (too high would make difficult to get results).
* `access_app`: {boolean} whether or not the result shouold be accessible from the producing app. Default is false.
* `access_public`: {boolean} whether or not the result should be accessible by any requesting organization. Default is false.
* `with_quartiles`: {boolean} when set to true, median, first quartile and third quartile will be computed alongside the other aggregates.
* `max_days_to_update_quartile`: {number} the maximum days a quartile can be safely updated after its first creation. Below this threshold, the measures cannot be purged. Default is 100.

Note there is no public API to insert a new definition. For security purposes, Cozy restricts this possibility and carefully evaluates each new measure definition to accept it or not.

## Aggregates functions

The available aggregates functions are the following:
- `sum`: the sum of values
- `count`: the number of values
- `count_not_zero`: the number of values different from zero.
- `min`: the minimum value
- `max`: the maximum value
- `avg`: the average of values
- `std`: the standard deviation
- `median`: the median of values. Only computed when `with_quartiles` is set in measure definition.
- `first_quartile`: The first quartile of values. Only computed when `with_quartiles` is set in measure definition.
- `third_quartile`: the third quartile of values. Only computed when `with_quartiles` is set in measure definition.


## Query an aggregated result

You can query the `/aggregate` endpoint to get an aggregated result:

```
$ curl -X GET -H 'Authorization: Bearer <token>' -H 'Content-Type: application/json' http://localhost:5000/aggregate -d '{"measureName": "connection-count-daily", "startDate": "2022-01-01", "endDate": "2022-01-02"}'
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 12
Server: Werkzeug/2.0.1 Python/3.8.10

[
  {
    "avg": 54.39,
    "count": 173,
    "countNotZero": 172,
    "createdBy": "ecolyo",
    "group1": {
      "device": "desktop"
    },
    "max": 100.0,
    "measureName": "connection-count-daily",
    "min": 0.0,
    "startDate": "2022-01-01T00:00:00",
    "std": 28.94,
    "sum": 9410.0
  },
  {
    "avg": 53.04,
    "count": 26,
    "countNotZero": 26,
    "createdBy": "ecolyo",
    "group1": {
      "device": "mobile"
    },
    "max": 94.0,
    "measureName": "connection-count-daily",
    "min": 3.0,
    "startDate": "2022-01-02T00:00:00",
    "std": 29.33,
    "sum": 1379.0
  }
]

```

The expected query parameters are the following:
* `measureName`: {string} the name of the measure. It must match an existing measure definition.
* `startDate`: {date} the start date of the requested time period.
* `endDate`: {date} the end date of the requested time period.
* `createdBy`: {string} [optionnal] the name of the application that produced the measure.

ℹ️ `startDate` is inclusive, while `endDate` is exclusive. In other words, `startDate >= {results} < endDate`

⚠️ If an aggregate has less contributions than the `aggregation_threshold` set in the associated measure definition, no result will be returned. This is a safeguard to ensure that no individual contribution can be revealed.

# Development

## Build and launch docker dev environment

To launch DACC application in developement environment with a dedicated PostgreSQL
database in a docker environment:

- Create `.env` development file containing

```
FLASK_ENV=development
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
PORT=5000
```

- Copy `config-template.yml` to `config.yml` (no need to change anything for dev)

```
$ cp config-template.yml config.yml
```

- Build app image and launch PostgreSQL and DACC

```
docker-compose up
```

The application should start in development environment with auto-reloading.
You can also add `-d` option if you prefer to launch it in background

## Execute tests

To execute tests while your docker dev environment is running, simply run

```
$ docker exec dacc_web pytest
```

## Docker dev environment stop & cleanup

To stop dev environment containers, run the following commands:

```
$ docker-compose down -v
```

To delete postgresql volumes, once stopped, use:

```
sudo rm -rf volumes
```

## Managing versions

DACC uses [semantic versioning](https://semver.org/), that is versions are in the form `<major>.<minor>.<patch>`.

- `<major>` is updated when there is breaking API changes
- `<minor>` is updated on feature addition
- `<patch>` is updated on backward-compatible bug fixes

### Releasing a new version

The script `scripts/releaseversion.sh` will release a new production version:
- Remove the `-dev` suffix to current version
- Commit & tag production version
- Bump to next development release (bumping `<patch>`, ready for next bugfix)
- Commit next development release
- Push commits & tags

```
$ ./scripts/releaseversion.sh
```

### Updating version number

Each time you introduce new features, you need to manually increase `<minor>` in version number (and reset patch to 0) and each time you introduce backward-incompatible API change, you need to bump `<major>` and reset minor and patch to 0.

To manually change version, use the script `scripts/nextversion.sh`

```
$ ./scripts/nextversion.sh 1.2.3
```

This script will update version number, adding `-dev` suffix but it is your responsibility to add, commit & push the change.

# Administration

## Healthchecks

You can query the `/status` route to get health checks result:

```
$ curl -s -i http://localhost:5000/status
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 63
Server: Werkzeug/2.0.1 Python/3.8.10

{
  "db": {
    "status": "ok"
  },
  "global_status": "ok"
}
```

Or If you need to only get the global status:

```
$ curl -s http://localhost:5000/status | jq -r '.global_status'
ok
```

## Authentication

Some routes need authentication. Some commands are available to set up token-based authentication:

```
flask token create # Create a new token linked to an organization
flask token get # Get the list of existing tokens
flask token update # Update a token linked to an organization
flask token delete-org # Remove an organization
```

## Database migration

When the database needs a migration, i.e. when the structure changed, for instance a new column, one needs to run `flask db migrate`. A migration script is then generated, that must be commited.

It is then possible to run `flask db upgrade` on the DACC server to automatically handle the database migration.

⚠️ Note the materialized views cannot be manually altered. Thus, a migration on the view will trigger a recreation from scratch, which can take some time depending on the volume.
Hence, the migration script might include the following steps to prevent any service interruption:
```
CREATE MATERIALIZED VIEW tmp AS ...;
DROP MATERIALIZED VIEW myView;
ALTER MATERIALIZED VIEW tmp RENAME TO myView;
```

## Insert definitions

To insert measure definitions, simply copy `assets/definitions-example.json`
to a new file, adapt it to suit your needs and
run `flask insert-definitions-json -f assets/yournewfile.json`.

Without the `-f` flag to specify a specific definition file, it takes the
JSON file stored in `dacc/assets/definitions.json` by default.

For each definition found, it either inserts it, if it does not exist,
or updates it otherwise.

## Definition removal

Definitions removed from file are not removed from database by
`insert-definitions-json`. Currently, definitions should be removed by
hand from database. A future cli command could be added to remove
definitions.

## Measures purge

Raw measures can be purged with the commands:

-  `flask purge measure <measure_name>`.
-  `flask purge all-measures`.

By default, measures oldest than 90 days will be deleted. 
A `-d days` option can be passed to specify the minimal age of a measure to be deleted, expressed in number of days, starting from the current date.


Note the measures involving quartiles cannot be purged as easily as the others, because quartiles cannot be partitioned: one needs all the measures to compute the quartile. Thus, the `max_days_to_update_quartile` is used to determine if the measures can be removed.

When measures are purged, the impacted aggregate are updated to save the purge date in the `last_raw_measures_purged` column.

## Logging

Simply enable the functionality in your config file and define minimum message criticity (in syslog's meaning) you want to be sent to syslog:

```
logging:
  enable: True
  logger_criticity: info
```

# Community

## What's Cozy?

<div align="center">
  <a href="https://cozy.io">
    <img src="https://cdn.rawgit.com/cozy/cozy-site/master/src/images/cozy-logo-name-horizontal-blue.svg" alt="cozy" height="48" />
  </a>
 </div>
 </br>

[Cozy] is a platform that brings all your web services in the same private space.  With it, your webapps and your devices can share data easily, providing you with a new experience. You can install Cozy on your own hardware where no one's tracking you.

### Maintainer

The lead maintainer for the DACC is [the Cozy Team](https://github.com/cozy).


### Get in touch

You can reach the Cozy Community by:

- Chatting with us on IRC [#cozycloud on Libera.Chat][libera]
- Posting on our [Forum][forum]
- Posting issues on the [Github repos][github]
- Say Hi! on [Twitter][twitter]


# License

DACC is developed by Cozy and distributed under the [AGPL v3 license][agpl-3.0].

[cozy]: https://cozy.io "Cozy Cloud"
[agpl-3.0]: https://www.gnu.org/licenses/agpl-3.0.html
[twitter]: https://twitter.com/cozycloud
[forum]: https://forum.cozy.io/
[github]: https://github.com/cozy/
[libera]: https://web.libera.chat/#cozycloud
