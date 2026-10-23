#!/bin/bash
# Stops only the two exact project-owned jobs through their ownership checks.
set -u

reviewradar_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)" || exit 1
cd "$reviewradar_root" || exit 1

finish() {
  if [ -t 0 ]; then
    printf '\nPress Return to close this launcher.\n'
    read -r _
  fi
  exit "$1"
}

printf 'Stop ReviewRadar local services\n\n'
printf 'This stops only this project\047s managed app and model in the current login session.\n'
printf 'It does not remove saved evidence or notes and does not stop unrelated applications.\n'
printf 'No login-startup item is installed or removed.\n\n'

if [ ! -x "$reviewradar_root/.venv/bin/python" ]; then
  printf 'The project Python environment is missing. See Run locally in:\n%s/README.md\n' "$reviewradar_root"
  printf 'No services were changed by this launcher.\n'
  finish 1
fi

"$reviewradar_root/.venv/bin/python" "$reviewradar_root/scripts/local_services.py" stop
reviewradar_result=$?
if [ "$reviewradar_result" -ne 0 ]; then
  printf '\nShutdown did not finish. Inspect the error above and current service status.\n'
  printf 'Do not stop other processes to work around an ownership or port warning.\n'
  printf 'Troubleshooting: %s/docs/16-RELIABILITY-AND-PRACTICAL-USE.md\n' "$reviewradar_root"
  finish "$reviewradar_result"
fi

printf '\nThis project\047s managed services are stopped.\n'
printf 'Double-click Start ReviewRadar.command when you want to resume.\n'
finish 0
