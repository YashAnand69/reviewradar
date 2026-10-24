#!/usr/bin/env python3
"""Record read-only availability during a user-run lifecycle check.

Run from your own Terminal, then quit the chat app and open ReviewRadar in an
independent browser. Endpoint health alone does not prove that quit occurred.
No session tokens, discussion contents or model credentials are recorded.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]


def probe() -> dict:
    result = {}
    opener = build_opener(ProxyHandler({}))
    for service, url in {
        "app": "http://127.0.0.1:8893/api/health",
        "model": "http://127.0.0.1:18085/health",
    }.items():
        try:
            with opener.open(url, timeout=2) as response:
                data = json.loads(response.read(8192))
                result[service] = {
                    "healthy": response.status == 200 and data.get("status") == "ok"
                }
        except (OSError, ValueError, AttributeError):
            result[service] = {"healthy": False}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=120)
    args = parser.parse_args()
    if not 5 <= args.seconds <= 300:
        parser.error("Choose 5–300 seconds")
    out = ROOT / "outputs/lifecycle"
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = out / f"availability-{stamp}-{os.getpid()}.json"
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "probe_pid": os.getpid(),
        "probe_parent_pid": os.getppid(),
        "limits": "Read-only endpoint samples; a human must separately record actual chat-app quit and independent browser behavior. No conclusion about ownership or fix correctness.",
        "samples": [],
        "completed": False,
    }
    deadline = time.monotonic() + args.seconds
    try:
        while True:
            report["samples"].append(
                {"at": datetime.now(timezone.utc).isoformat(), "endpoints": probe()}
            )
            destination.write_text(json.dumps(report, indent=2) + "\n")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(5, remaining))
        report["completed"] = True
    except KeyboardInterrupt:
        report["interrupted"] = True
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        destination.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Availability record: {destination}")
    print(
        "Record actual quit time and independent browser result separately; this is not an automatic certification."
    )
    return 0 if report["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
