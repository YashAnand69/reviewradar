#!/bin/bash
# Read captured discussions without downloading or starting a model.
set -eu
reviewradar_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$reviewradar_root"
if [ ! -x .venv/bin/python ]; then
  printf 'Run first-time setup from README.md before starting ReviewRadar.\n'
  exit 1
fi
.venv/bin/python scripts/doctor.py
printf '\nOpening a local reading service at http://127.0.0.1:8893/\n'
printf 'Keep this Terminal open. Ctrl+C stops it. No model is downloaded or started.\n'
printf 'If the port is already in use, use the existing workspace; no existing service will be stopped.\n'
export PYTHONPATH="$reviewradar_root/backend"
exec .venv/bin/python -m reviewradar
