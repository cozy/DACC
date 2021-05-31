#!/bin/bash

set -e

SCRIPT_DIR=$( cd "$(dirname "$0")" ; pwd -P )

usage () {
  echo "Usage: $0 <version>" >&2
  echo "  Create a new development version (prepare for next version)" >&2
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

if ! [[ ${1} =~ ^[0-9] ]]; then
  echo "Version must start with a digit" >&2
  usage
  exit 1
fi

echo "Updating version"
echo "__version__ = \"${1}-dev\"" > "${SCRIPT_DIR}/../dacc/version.py"
