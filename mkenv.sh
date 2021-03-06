#!/bin/bash

usage() {
  echo "Usage: $0 [-h/--help] [-r/--rebuild] [-u/--update] [VENV_DIR]"
  echo ""
  echo "Positional prameter:"
  echo "	VENV_DIR		Directory in which creating virtual env (venv by default)"
  echo ""
  echo "Options:"
  echo "	-h / --help		Print usage message and exit"
  echo "	-r / --rebuild		Force venv rebuild, even if it exists"
  echo "	-u / --update		Update venv from requirements.txt"
}

install_venv() {
  source "${1}/bin/activate"
  pip install wheel
  pip install -r "${2}/requirements.txt"
}

MYDIR=$(dirname $0)

# Options parsing
REBUILD=false
UPDATE=false
PARSED_OPTIONS=$(getopt -n "$0"  -o hru --long "help,rebuild,update"  -- "$@")

if [ $? -ne 0 ];
then
  echo "" >&2
  usage >&2
  exit 1
fi

eval set -- "$PARSED_OPTIONS"

while true; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -r|--rebuild)
      REBUILD=true
      shift
      ;;
    -u|--update)
      UPDATE=true
      shift
      ;;
    --)
     shift
     break
     ;;
  esac
done

if [ -n "${1}" ]; then
  VENVDIR="${1}"
else
  VENVDIR="${MYDIR}/venv"
fi

if ${REBUILD}; then
  echo "Removing old venv"
  rm -rf "${VENVDIR}"
fi

if [ ! -d "${VENVDIR}" ]; then
  echo "Creating virtual env"
  python3 -m venv "${VENVDIR}"
  install_venv "${VENVDIR}" "${MYDIR}"
elif ${UPDATE}; then
  echo "Updating existing virtual env"
  install_venv "${VENVDIR}" "${MYDIR}"
else
  echo "Virtual env already exist, nothing to do"
fi

echo "Virtual env ready, activate with source venv/bin/activate"
