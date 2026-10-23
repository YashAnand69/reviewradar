#!/usr/bin/env python3
"""Explicit local recovery check. Restarts only this project's managed services.

No GitHub writes. Proves stale-session rejection and source/decision persistence
through a stop/start cycle; does not claim browser or human usability validation.
"""

import json
from pathlib import Path
import subprocess
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    command = [sys.executable, str(ROOT / "scripts/local_services.py")]
    state = json.loads(subprocess.check_output([*command, "status"], text=True))
    if not all(
        item["managed"] and item["healthy"] for item in state["services"].values()
    ):
        raise SystemExit(
            "Start this project’s managed services before this explicit recovery check."
        )
    with httpx.Client(base_url=state["url"], timeout=20, trust_env=False) as client:
        token = client.get("/runtime-config").json()["api_token"]
        client.headers.update(
            {"X-ReviewRadar-Token": token, "Origin": state["url"].rstrip("/")}
        )
        packet = client.get("/api/sample")
        packet.raise_for_status()
        packet = packet.json()
        analysis = packet["analysis"]
        path = f"/api/analyses/{analysis['id']}/dispositions"
        before = client.get(path)
        before.raise_for_status()
        dispositions = before.json()
        subprocess.run([*command, "stop"], cwd=ROOT, check=True, capture_output=True)
        try:
            client.get("/api/health", timeout=2)
        except httpx.HTTPError:
            stopped = True
        else:
            stopped = False
        restarted = subprocess.run(
            [*command, "start"], cwd=ROOT, capture_output=True, text=True
        )
        if restarted.returncode:
            raise SystemExit(
                "Recovery check could not restart the local services: "
                + restarted.stderr.strip()
            )
        assert stopped, "Stopped service still responded; inspect port ownership."
        rejected = client.get(path)
        assert rejected.status_code == 401, "Stale session was not rejected."
        token = client.get("/runtime-config").json()["api_token"]
        client.headers["X-ReviewRadar-Token"] = token
        after = client.get(path)
        after.raise_for_status()
        assert after.json() == dispositions, "Stored decisions changed during restart."
        source = client.get(f"/api/snapshots/{packet['snapshot']['id']}")
        source.raise_for_status()
        assert source.json() == packet["snapshot"], "Snapshot changed during restart."
        health = client.get("/api/health").json()
        assert health["status"] == "ok" and health["model_ready"]
    result = {
        "checks": [
            "managed stop made the local API unavailable",
            "saved-path startup restored both project-owned services",
            "stale browser token rejected before protected reads or writes",
            "new session restored identical stored decisions",
            "immutable snapshot survived restart",
            "actual model identity/context readiness verified",
        ],
        "analysis_id": analysis["id"],
        "snapshot_id": packet["snapshot"]["id"],
        "limits": "Local service/HTTP boundary check; not rendered browser verification or a genuine-user trial.",
    }
    (ROOT / "outputs/service-recovery.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
