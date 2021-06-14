#!/bin/sh

set -o errexit

flask db upgrade
exec "$@"
