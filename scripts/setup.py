#!/usr/bin/env python3
"""Explicitly install locked dependencies and build the local interface."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--node", type=Path, help="Optional path to a supported Node executable"
    )
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        raise SystemExit(
            "Run setup with Python 3.12; other versions have not been verified."
        )
    environment = dict(os.environ)
    if args.node:
        node = args.node.expanduser().resolve()
        if not node.is_file():
            parser.error("The supplied Node executable does not exist.")
        environment["PATH"] = (
            str(node.parent) + os.pathsep + environment.get("PATH", "")
        )
    node_command = shutil.which("node", path=environment.get("PATH"))
    npm_command = shutil.which("npm", path=environment.get("PATH"))
    if not node_command or not npm_command:
        raise SystemExit(
            "Install Node 24 LTS with npm, then retry. Setup will not install a system runtime."
        )
    version = subprocess.check_output(
        [node_command, "--version"], text=True, env=environment
    ).strip()
    pieces = tuple(int(n) for n in version.lstrip("v").split("."))
    if pieces < (24, 15, 0):
        raise SystemExit(
            f"Node {version} is unsupported. Use Node 24.15+ LTS (the complete test setup includes jsdom)."
        )
    venv = ROOT / ".venv"
    if not venv.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "-r", "requirements-lock.txt"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [npm_command, "ci"], cwd=ROOT / "frontend", env=environment, check=True
    )
    subprocess.run(
        [npm_command, "run", "build"],
        cwd=ROOT / "frontend",
        env=environment,
        check=True,
    )
    print(
        "Local interface built. Start the app using PYTHONPATH=backend .venv/bin/python -m reviewradar."
    )
    print(
        "Model setup is separate and explicit; the chronology baseline does not require model weights."
    )


if __name__ == "__main__":
    main()
