# DACC

The Data Aggregator Cross Cozy (DACC)

## Setup

### Install

To setup the environement and install dependencies, simply run:

```
./mkenv.sh
```

### Config

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
flask add-token # Add a new token linked to an organization
flask get-token # Get the list of existing tokens
flask update-token # Update a token linked to an organization
flask delete-org # Remove an organization
```



## Add a measure

You can query the `/measure` endpoint:

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

The `token` is the one specified in your remote-doctype to authenticate the stack. See the [authentication](#authentication) section

## Development

### Build and launch docker dev environment

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

### Execute tests

To execute tests while your docker dev environment is running, simply run

```
$ docker exec dacc_web pytest
```

### Docker dev environment stop & cleanup

To stop dev environment containers, run the following commands:

```
$ docker-compose down -v
```

To delete postgresql volumes, once stopped, use:

```
sudo rm -rf volumes
```

### Managing versions

DACC uses [semantic versioning](https://semver.org/), that is versions are in the form `<major>.<minor>.<patch>`.

- `<major>` is updated when there is breaking API changes
- `<minor>` is updated on feature addition
- `<patch>` is updated on backward-compatible bug fixes

#### Releasing a new version

The script `scripts/releaseversion.sh` will release a new production version:
- Remove the `-dev` suffix to current version
- Commit & tag production version
- Bump to next development release (bumping `<patch>`, ready for next bugfix)
- Commit next development release
- Push commits & tags

```
$ ./scripts/releaseversion.sh
```

#### Updating version number

Each time you introduce new features, you need to manually increase `<minor>` in version number (and reset patch to 0) and each time you introduce backward-incompatible API change, you need to bump `<major>` and reset minor and patch to 0.

To manually change version, use the script `scripts/nextversion.sh`

```
$ ./scripts/nextversion.sh 1.2.3
```

This script will update version number, adding `-dev` suffix but it is your responsibility to add, commit & push the change.

## Database migration

When the database needs a migration, i.e. when the structure changed, for instance a new column, one needs to run `flask db migrate`. A migration script is then generated, that must be commited.

It is then possible to run `flask db update` on the DACC server to automatically handle the database migration. 