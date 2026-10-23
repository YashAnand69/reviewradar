#!/usr/bin/env python3
"""Exercise the running local app; never writes to GitHub.

--model runs actual local inference. --live-github additionally imports one public
authored PR. Without either flag this only exercises the bundled saved sample,
local decision/reopen, baseline and export paths.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="store_true")
    parser.add_argument("--live-github", action="store_true")
    args = parser.parse_args()
    checks = []
    with httpx.Client(
        base_url="http://127.0.0.1:8893", timeout=240, trust_env=False
    ) as client:
        client.get("/api/health").raise_for_status()
        config = client.get("/runtime-config").json()
        client.headers.update(
            {
                "X-ReviewRadar-Token": config["api_token"],
                "Origin": "http://127.0.0.1:8893",
            }
        )
        response = client.get("/api/sample")
        response.raise_for_status()
        sample = response.json()
        checks.append("saved sample loads with validated bound evidence")
        analysis = sample["analysis"]
        card = analysis["cards"][0]
        path = f"/api/analyses/{analysis['id']}/cards/{card['id']}/disposition"
        previous = next(
            (
                item
                for item in client.get(
                    f"/api/analyses/{analysis['id']}/dispositions"
                ).json()
                if item["card_id"] == card["id"]
            ),
            None,
        )
        response = client.put(
            path, json={"state": "reviewed", "note": "Smoke test; no GitHub change."}
        )
        response.raise_for_status()
        assert response.json()["state"] == "reviewed"
        restored = (
            {"state": previous["state"], "note": previous["note"]}
            if previous
            else {"state": "open", "note": ""}
        )
        client.put(path, json=restored).raise_for_status()
        checks.append("local decision save and reopen; pre-existing note restored")
        exported = client.get(f"/api/analyses/{analysis['id']}/export")
        exported.raise_for_status()
        assert "not verification of a code fix" in exported.text
        assert "NO — inspect incomplete sources" in exported.text
        checks.append("Markdown export retains source limits and interpretation caveat")
        source = sample["snapshot"]
        if args.live_github:
            response = client.post(
                "/api/snapshots/github",
                json={
                    "owner": "YashAnand69",
                    "urls": ["https://github.com/fossasia/eventyay/pull/6104"],
                },
            )
            response.raise_for_status()
            source = response.json()
            assert source["complete"] and len(source["prs"][0]["comments"]) >= 9
            checks.append(
                "fresh read-only public GitHub intake: comments, reviews and inline/thread coverage"
            )
        mode = "model" if args.model else "baseline"
        response = client.post(
            "/api/analyses", json={"snapshot_id": source["id"], "mode": mode}
        )
        response.raise_for_status()
        result = response.json()
        assert result["mode"] == mode
        assert all(item["status"] == "analyzed" for item in result["coverage"])
        assert result["cards"]
        checks.append(f"actual {mode} analysis saves and restores through the API")
        assert (
            client.get(f"/api/analyses/{result['id']}").json()["snapshot_id"]
            == source["id"]
        )
        assert client.get(f"/api/analyses/{result['id']}/dispositions").json() == []
        checks.append("new analysis starts with independent local decisions")
    report = {
        "at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "analysis_id": result["id"],
        "mode": mode,
        "live_github": args.live_github,
        "cards": len(result["cards"]),
        "seconds": result["stats"]["elapsed_seconds"],
        "limits": "HTTP integration check only; not visual, keyboard, mobile or human usability validation.",
    }
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    (output / "actual-api-smoke.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
