#!/bin/bash
# Double-click in Finder to run from Terminal, rather than from the chat app.
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

printf 'ReviewRadar local workspace\n\n'
printf 'Run this file by double-clicking it in Finder or from your own Terminal.\n'
printf 'It restarts this project\047s owned services outside the chat app to avoid chat attribution.\n'
printf 'Persistence after quitting ChatGPT still needs verification; it is not guaranteed.\n'
printf 'Saved evidence and notes are preserved; an in-flight analysis may be interrupted.\n'
printf 'This does not install login startup.\n'
printf 'The services use this macOS login session; start again after logout or reboot.\n'
printf 'Saved model/runtime paths are used. No downloads or purchases are performed.\n\n'

if [ ! -x "$reviewradar_root/.venv/bin/python" ]; then
  printf 'The project Python environment is missing. Complete Run locally in:\n%s/README.md\n' "$reviewradar_root"
  finish 1
fi

if [ ! -f "$reviewradar_root/.runtime/services/config.json" ]; then
  printf 'First-time service setup is required. See Run locally in:\n%s/README.md\n\n' "$reviewradar_root"
  printf 'From this project folder, start once with your explicit model/runtime paths:\n'
  printf '.venv/bin/python scripts/local_services.py start --runtime /absolute/path/to/llama-server --model /absolute/path/to/model.gguf\n'
  finish 1
fi

# Check saved paths before interrupting any currently working services.
"$reviewradar_root/.venv/bin/python" "$reviewradar_root/scripts/local_services.py" check
reviewradar_result=$?
if [ "$reviewradar_result" -ne 0 ]; then
  printf '\nStartup prerequisites are not ready. Existing services were not stopped.\n'
  finish "$reviewradar_result"
fi

# Reusing already-running jobs would retain their original app attribution.
# Stop only the exact owned jobs, and require completed teardown before start.
"$reviewradar_root/.venv/bin/python" "$reviewradar_root/scripts/local_services.py" stop
reviewradar_result=$?
if [ "$reviewradar_result" -ne 0 ]; then
  printf '\nThe existing services could not be safely stopped. No replacement was started.\n'
  printf 'Inspect the error above and run: .venv/bin/python scripts/local_services.py status\n'
  finish "$reviewradar_result"
fi

"$reviewradar_root/.venv/bin/python" "$reviewradar_root/scripts/local_services.py" start
reviewradar_result=$?
if [ "$reviewradar_result" -ne 0 ]; then
  printf '\nStartup did not finish. Read the error above; do not stop unrelated applications.\n'
  printf 'For current state, run: .venv/bin/python scripts/local_services.py status\n'
  printf 'Troubleshooting: %s/docs/16-RELIABILITY-AND-PRACTICAL-USE.md\n' "$reviewradar_root"
  finish "$reviewradar_result"
fi

printf '\nWorkspace ready: http://127.0.0.1:8893/\n'
printf 'Return to your open browser tab and choose Retry connection, or open that address.\n'
printf 'Closing this launcher window does not request service shutdown.\n'
printf 'Use Stop ReviewRadar.command when you want to stop this project.\n'
finish 0
