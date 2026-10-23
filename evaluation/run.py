#!/usr/bin/env python3
"""Reproduce a frozen pilot run. No automatic accuracy or human-savings claim.

Run from the repository root with PYTHONPATH=backend. Complete source snapshots
remain local; hashes and original URLs are recorded in dataset-manifest.json.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess

from reviewradar.analysis import run_analysis, validate_bound_analysis
from reviewradar.config import Settings
from reviewradar.model import PROMPT_VERSION, SYSTEM_PROMPT, LINK_PROMPT
from reviewradar.schemas import normalize_snapshot

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=["development", "holdout"], required=True)
    parser.add_argument(
        "--iteration",
        default="initial",
        help="Distinct preserved run name; never relabel a tuned holdout as untouched",
    )
    args = parser.parse_args()
    if not args.iteration.replace("-", "").isalnum():
        parser.error("Iteration must contain letters, digits or hyphens")
    manifest = json.loads((ROOT / "evaluation/dataset-manifest.json").read_text())
    labels_path = ROOT / f"evaluation/labels-{args.split}.json"
    expected_label_hash = next(
        item["sha256"]
        for item in manifest["label_files"]
        if item["path"] == str(labels_path.relative_to(ROOT))
    )
    if hashlib.sha256(labels_path.read_bytes()).hexdigest() != expected_label_hash:
        raise SystemExit(
            "Frozen label file changed. Record a new iteration rather than overwriting a holdout claim."
        )
    labels = json.loads(labels_path.read_text())
    output = ROOT / "outputs/evaluation" / args.split / args.iteration
    output.mkdir(parents=True, exist_ok=True)
    if (output / "run-manifest.json").exists():
        raise SystemExit(
            "This split already has a saved run. Preserve it; choose a separately documented new iteration."
        )
    results = []
    for record in manifest["raw_snapshots"]:
        if record["pr_id"] not in labels["prs"]:
            continue
        path = ROOT / record["local_ignored_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise SystemExit(f"Source snapshot changed: {record['pr_id']}")
        snapshot = normalize_snapshot(json.loads(path.read_text()))
        analysis = run_analysis(snapshot, "model", Settings())
        validate_bound_analysis(analysis, snapshot)
        baseline = run_analysis(snapshot, "baseline", Settings())
        stem = record["pr_id"].replace("/", "-").replace("#", "-")
        (output / f"{stem}-model.json").write_text(analysis.model_dump_json(indent=2))
        (output / f"{stem}-baseline.json").write_text(
            baseline.model_dump_json(indent=2)
        )
        results.append(
            {
                "pr_id": record["pr_id"],
                "snapshot_id": snapshot.id,
                "analysis_id": analysis.id,
                "complete": analysis.complete,
                "model_cards": len(analysis.cards),
                "baseline_comments": len(baseline.cards),
                "seconds": analysis.stats.elapsed_seconds,
                "coverage": [item.model_dump() for item in analysis.coverage],
            }
        )
        print(json.dumps(results[-1]), flush=True)
    run = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "split": args.split,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": hashlib.sha256(
            (SYSTEM_PROMPT + LINK_PROMPT).encode()
        ).hexdigest(),
        "implementation_sha256": hashlib.sha256(
            (ROOT / "backend/reviewradar/model.py").read_bytes()
        ).hexdigest(),
        "labels_sha256": expected_label_hash,
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "results": results,
        "limitations": "Engineering pilot. Semantic scoring requires case-level review; no participant timing or population accuracy claim.",
    }
    (output / "run-manifest.json").write_text(json.dumps(run, indent=2) + "\n")


if __name__ == "__main__":
    main()
