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

You can query the `/status` route to get health checks result
