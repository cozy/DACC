#!/bin/bash

set -e

SCRIPT_DIR=$( cd "$(dirname "$0")" ; pwd -P )

usage () {
  echo "Usage: $0" >&2
  echo "  Release a new production version" >&2
}

echo "Updating version"
sed -i -e 's/-dev//' "${SCRIPT_DIR}/../dacc/version.py"
git add "${SCRIPT_DIR}/../dacc/version.py"
pushd "${SCRIPT_DIR}/.."
VERSION=$(./venv/bin/python -c 'from dacc.version import __version__; print(__version__)')
git commit -m "Release v${VERSION}"
git tag "v${VERSION}"
popd

echo "Bump to next dev version"
MAJOR="$(echo "${VERSION}" | cut -d. -f1)"
MINOR="$(echo "${VERSION}" | cut -d. -f2)"
PATCH="$(echo "${VERSION}" | cut -d. -f3)"
NEXTPATCH="$((PATCH + 1))"
NEXTVERSION="${MAJOR}.${MINOR}.${NEXTPATCH}"
echo "  Next version will be ${NEXTVERSION}"
"${SCRIPT_DIR}/nextversion.sh" "${NEXTVERSION}"
git add "${SCRIPT_DIR}/../dacc/version.py"
git commit -m "chore: Bump version to ${NEXTVERSION}-dev"

echo "Pushing changes to repo"
git push --set-upstream origin master
git push --tags
