#!/usr/bin/env python3
"""Read-only, offline setup diagnosis. Never downloads, starts or stops services.

The optional --verify-artifacts flag reads the configured model/runtime bytes.
No credentials, source discussions or machine-specific paths are printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def command(arguments, timeout=15):
    try:
        result = subprocess.run(
            arguments, capture_output=True, text=True, timeout=timeout, check=False
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inspect(root=ROOT, verify_artifacts=False, node=None):
    root = Path(root).resolve()
    checks = []

    def add(name, status, detail, action=""):
        checks.append(dict(name=name, status=status, detail=detail, action=action))
        return status == "ready"

    python = root / (
        ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python"
    )
    python_ready = False
    if not python.is_file() or not os.access(python, os.X_OK):
        add(
            "Python environment",
            "missing",
            "The project environment is absent or not executable.",
            "Install Python 3.12 and Node 24.15+ LTS, then run: python3.12 scripts/setup.py",
        )
    else:
        requirements = {}
        try:
            for line in (root / "requirements-lock.txt").read_text().splitlines():
                if line.strip() and not line.lstrip().startswith("#"):
                    name, version = line.split("==", 1)
                    requirements[name] = version
            probe = "import importlib.metadata as m,json,sys; names=json.loads(sys.argv[1]); installed={d.metadata['Name'].lower().replace('_','-'):d.version for d in m.distributions()}; print(json.dumps({'python':list(sys.version_info[:2]),'mismatches':[n for n,v in names.items() if installed.get(n.lower().replace('_','-'))!=v]}))"
            output = command([str(python), "-I", "-c", probe, json.dumps(requirements)])
            result = json.loads(output or "{}")
            python_ready = (
                result.get("python") == [3, 12]
                and result.get("mismatches") == []
                and bool(requirements)
            )
            add(
                "Python environment",
                "ready" if python_ready else "repair",
                "Python 3.12 and every locked distribution match."
                if python_ready
                else "Python version or locked dependencies do not match, or the probe failed.",
                ""
                if python_ready
                else "Run: python3.12 scripts/setup.py (use --node /path/to/node if Node is not on PATH).",
            )
        except (OSError, ValueError, TypeError):
            add(
                "Python environment",
                "repair",
                "Could not validate the environment against requirements-lock.txt.",
                "Restore the lockfile and run: python3.12 scripts/setup.py",
            )

    dist = root / "frontend/dist"
    frontend_ready = False
    try:
        index = (dist / "index.html").read_text()
        assets = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', index)
        local_assets = [asset for asset in assets if asset.endswith((".js", ".css"))]
        frontend_ready = bool(local_assets) and all(
            (dist / asset.removeprefix("./")).resolve().is_relative_to(dist.resolve())
            and (dist / asset.removeprefix("./")).is_file()
            for asset in local_assets
        )
    except (OSError, ValueError):
        pass
    add(
        "Built interface",
        "ready" if frontend_ready else "missing",
        "The built page and referenced script/style files exist."
        if frontend_ready
        else "The built page or its script/style files are missing.",
        "" if frontend_ready else "Run: python3.12 scripts/setup.py",
    )

    node_command = str(node) if node else shutil.which("node")
    node_version = command([node_command, "--version"]) if node_command else None
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", node_version or "")
    node_ready = bool(
        match and int(match[1]) == 24 and (int(match[2]), int(match[3])) >= (15, 0)
    )
    npm = (
        shutil.which(
            "npm", path=str(Path(node).parent) + os.pathsep + os.environ.get("PATH", "")
        )
        if node
        else shutil.which("npm")
    )
    add(
        "Build tools",
        "ready" if node_ready and npm else "optional",
        "Node 24.15+ and npm are available."
        if node_ready and npm
        else "A verified Node 24.15+ LTS/npm pair was not found. Already-built source reading does not require them.",
        ""
        if node_ready and npm
        else "For installation or rebuilding, install Node 24 LTS with npm; pass --node /absolute/path/to/node when it is outside PATH.",
    )

    gh = shutil.which("gh")
    gh_ready = bool(gh and command([gh, "--version"]))
    add(
        "Public GitHub import",
        "available" if gh_ready else "optional",
        "GitHub CLI is installed. Authentication and network access were not tested offline."
        if gh_ready
        else "GitHub CLI is unavailable. Saved snapshots and the public replay still work.",
        "For live import, install GitHub CLI, then run gh auth status in your Terminal. If needed, run gh auth login yourself.",
    )

    artifacts_ready = False
    try:
        config_path = root / ".runtime/services/config.json"
        if config_path.stat().st_size > 8192:
            raise ValueError("Oversized config")
        config = json.loads(config_path.read_text())
        if (
            not isinstance(config, dict)
            or set(config) != {"model", "runtime"}
            or not all(isinstance(v, str) and v for v in config.values())
        ):
            raise ValueError("Invalid config")
        manifest = json.loads((root / "model-manifest.json").read_text())
        model, runtime = (
            Path(config[key]).expanduser() for key in ("model", "runtime")
        )
        present = (
            model.is_file()
            and model.stat().st_size == manifest["model_bytes"]
            and runtime.is_file()
            and os.access(runtime, os.X_OK)
        )
        if not present:
            add(
                "Local inference artifacts",
                "missing",
                "Configured weights/runtime are absent, the model size differs, or the runtime is not executable.",
                "Check the pinned model/runtime instructions in README.md. Reconfigure their absolute paths using scripts/local_services.py foreground --runtime /path/to/llama-server --model /path/to/model.gguf",
            )
        elif not verify_artifacts:
            add(
                "Local inference artifacts",
                "unchecked",
                "Configured files exist and model size matches. Their identity has not been checked.",
                "Run: python3 scripts/doctor.py --verify-artifacts. This reads about 2.84 GB without downloading or launching anything.",
            )
        elif digest(model) != manifest["model_sha256"]:
            add(
                "Local inference artifacts",
                "repair",
                "The model checksum does not match the pinned artifact.",
                "Do not use these weights. Obtain the pinned artifact using scripts/download_model.py and reconfigure its path.",
            )
        elif digest(runtime) != manifest["runtime_verified_binary_sha256"]:
            add(
                "Local inference artifacts",
                "unchecked",
                "Model checksum matches; runtime differs from the tested macOS binary. It may be a valid source build.",
                "Use scripts/run_model.py for the pinned source-commit check. Doctor does not execute an unverified runtime.",
            )
        else:
            artifacts_ready = add(
                "Local inference artifacts",
                "ready",
                "Model and tested runtime checksums match the manifest. Running-service readiness is separate.",
            )
    except (OSError, ValueError, TypeError, KeyError):
        add(
            "Local inference artifacts",
            "optional",
            "No valid saved model/runtime configuration was found. Source reading needs no model.",
            "Follow README.md for explicit model/runtime setup. Nothing will be downloaded automatically.",
        )

    source_ready = (
        python_ready
        and frontend_ready
        and (root / "backend/reviewradar/__main__.py").is_file()
    )
    return dict(
        offline=True,
        read_only=True,
        source_reading_ready=source_ready,
        inference_artifacts_verified=artifacts_ready,
        checks=checks,
        next_step="Start source reading: PYTHONPATH=backend .venv/bin/python -m reviewradar"
        if source_ready
        else "Complete the missing required setup checks above, then run this doctor again.",
        limits="This checks local files and installed tools, not running services, network authentication, fresh-machine usability, model accuracy or survival after quitting another app.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-artifacts",
        action="store_true",
        help="Read model/runtime files to compare pinned SHA-256 identities",
    )
    parser.add_argument("--node", type=Path, help="Node executable outside PATH")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable status without credentials or configured paths",
    )
    args = parser.parse_args()
    result = inspect(verify_artifacts=args.verify_artifacts, node=args.node)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("ReviewRadar setup check — offline, read-only\n")
        for check in result["checks"]:
            print(f"[{check['status'].upper()}] {check['name']}: {check['detail']}")
            if check["action"]:
                print(f"  Next: {check['action']}")
        print("\n" + result["next_step"])
        print("\n" + result["limits"])
    return 0 if result["source_reading_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
