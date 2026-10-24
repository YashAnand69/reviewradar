#!/usr/bin/env python3
"""Run a named, frozen candidate once; preserve every attempt without user DB writes."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

from reviewradar.analysis import run_analysis, validate_bound_analysis
from reviewradar.config import Settings
from reviewradar.model import LINK_PROMPT, PROMPT_VERSION, SYSTEM_PROMPT
from reviewradar.schemas import normalize_snapshot

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--kind",
        choices=["development-regression", "unseen-engineering"],
        required=True,
    )
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text())
    manifest = json.loads(args.manifest.read_text())
    frozen = args.manifest.parent
    checks = [
        (
            ROOT / "backend/reviewradar/model.py",
            candidate["model_implementation_sha256"],
        ),
        (frozen / "labels.json", manifest["labels_sha256"]),
        (frozen / "PROTOCOL.md", manifest["protocol_sha256"]),
    ]
    for item in manifest["selected"]:
        checks.append((ROOT / item["path"], item["sha256"]))
    for path, digest in checks:
        if sha(path) != digest:
            raise SystemExit(f"Frozen artifact changed: {path}")
    if PROMPT_VERSION != candidate["prompt_version"]:
        raise SystemExit("Candidate version changed")
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "run-manifest.json"
    if path.exists() or list(args.output.glob("*-model.json")):
        raise SystemExit("Run artifacts already exist. Preserve the initial attempt.")
    config = json.loads((ROOT / ".runtime/services/config.json").read_text())
    settings = Settings()
    report = dict(
        started_at=datetime.now(timezone.utc).isoformat(),
        kind=args.kind,
        manifest_sha256=sha(args.manifest),
        labels_sha256=manifest["labels_sha256"],
        candidate=candidate,
        prompt_sha256=hashlib.sha256(
            (SYSTEM_PROMPT + LINK_PROMPT).encode()
        ).hexdigest(),
        model_sha256=sha(Path(config["model"])),
        runtime_sha256=sha(Path(config["runtime"])),
        settings=dict(
            context=settings.model_context,
            max_output=settings.model_output,
            margin=settings.model_margin,
            temperature=0,
            timeout=settings.model_timeout,
        ),
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        results=[],
        complete=False,
    )
    path.write_text(json.dumps(report, indent=2) + "\n")
    for item in manifest["selected"]:
        if (
            sha(ROOT / "backend/reviewradar/model.py")
            != candidate["model_implementation_sha256"]
        ):
            raise SystemExit("Candidate changed during run; no further calls")
        snapshot = normalize_snapshot(json.loads((ROOT / item["path"]).read_text()))
        stem = item["pr_id"].replace("/", "-").replace("#", "-")
        row = dict(
            pr_id=item["pr_id"],
            snapshot_id=snapshot.id,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        started = time.monotonic()
        try:
            analysis = run_analysis(snapshot, "model", settings)
            (args.output / f"{stem}-model.json").write_text(
                analysis.model_dump_json(indent=2) + "\n"
            )
            validate_bound_analysis(analysis, snapshot)
            row.update(
                complete=analysis.complete,
                cards=len(analysis.cards),
                mechanical_validation="pass",
                analysis_id=analysis.id,
                coverage=[x.model_dump() for x in analysis.coverage],
            )
        except Exception as exc:
            row.update(complete=False, error_type=type(exc).__name__)
        row["wall_seconds"] = round(time.monotonic() - started, 3)
        baseline = run_analysis(snapshot, "baseline", settings)
        validate_bound_analysis(baseline, snapshot)
        (args.output / f"{stem}-baseline.json").write_text(
            baseline.model_dump_json(indent=2) + "\n"
        )
        row["baseline_cards"] = len(baseline.cards)
        report["results"].append(row)
        path.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(row), flush=True)
    report.update(complete=True, finished_at=datetime.now(timezone.utc).isoformat())
    path.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
