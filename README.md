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
Date: Sun, 30 May 2021 13:22:24 GMT

{
  "ok": "true"
}

```

ℹ️ If you want to request an actual server, replace `http://localhost:5000/measure` by the actual URL, e.g. `https://dacc.cozycloud.cc/measure`, or `https://dacc-dev.cozycloud.cc/measure` for tests. 


ℹ️ The `token` is automatically injected by the stack when using a  remote-doctype. Here is the [remote-doctype](https://github.com/cozy/cozy-doctypes/tree/master/cc.cozycloud.dacc) that must be used to request the Cozy's DACC server. You can also use the one [for developement](https://github.com/cozy/cozy-doctypes/tree/master/cc.cozycloud.dacc-dev).
To know how to use a remote-doctype from a Cozy app, see the [stack documentation](https://docs.cozy.io/en/cozy-stack/remote/).

### Measure format 

Here is an example of a valid measure:
```
{
  "measureName": "connection-count-daily",
  "value": 6,
  "startDate": "2021-05-04",
  "createdBy": "ecolyo",
  "groups": [
    {
      "device": "desktop"
    }
  ]
}
```

The expected fields are the following:
* `measureName`: {string} the name of the measure. It must match an existing measure name on the DACC server.
* `value`: {number} the measured value. It can be 0 but never `null`.
* `startDate`: {date} the starting date of the measure. It must be set in relation with the `aggregationPeriod` for this measure. 
* `createdBy`: {string} the application that produced the measure.
* `groups`: {Array} a list of groups, used to group measures depending on attributes specified in the measure definition. Each group is a key-value entry, where the key is set in the measure definition. For example, `{"device": "desktop"}`. Note the `groups` length cannot exceed 3 and the order matters: the first key entry must match the `group1_key` of the measure definition, and so on. 



## Measure definition

A measure is defined by the following fields: 
* `name`: {string} the name of the measure. It must indicate what is measured and should include the aggregation period, if relevant, e.g. "connexion-daily", "konnector-error-monthly", etc.
* `org`: {string} the organization defining this measure.
* `group1_key`: {string}: the first grouping key. 
* `group2_key`: {string}: the second grouping key. 
* `group3_key`: {string}: the third grouping key.
* `description`: {string}: a human-readable description of the measure.
* `aggregation_period`: {string}: the period on which is computed the raw measure on the app side. It can be `day`, `week`, `month`.
* `execution_frequency`: {string}: the frequency on which the measure should be computed on the DACC. It can be `day`, `week`, `month`.
* `access_app`: {boolean}: whether or not the result shouold be accessible from the producing app.
* `access_public`: {boolean}: whether or not the result should be accessible by any requesting organization.

Note there is no public API to insert a new definition. For security purposes, Cozy restricts this possibility and carefully evaluates each new measure definition to accept it or not.


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
Date: Sun, 30 May 2021 13:22:24 GMT

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

It is then possible to run `flask db update` on the DACC server to automatically handle the database migration. 

## Insert definitions

To insert measure definitions, simply run `flask insert-definitions-json`.
By default, it takes the JSON file stored in `dacc/assets/definitions.json`, containing all definitions.

For each definition found, it either inserts it, if it does not exist, or updates it otherwise.


