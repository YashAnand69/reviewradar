#!/usr/bin/env python3
"""Build the explicitly historical public replay without replacing local UI."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", type=Path)
    args = parser.parse_args()
    env = dict(os.environ)
    env["VITE_REPLAY"] = "1"
    if args.node:
        env["PATH"] = (
            str(args.node.expanduser().resolve().parent)
            + os.pathsep
            + env.get("PATH", "")
        )
    npm = shutil.which("npm", path=env["PATH"])
    if not npm:
        raise SystemExit("npm is required. Run the documented setup first.")
    destination = ROOT / ".runtime/replay-dist"
    subprocess.run(
        [npm, "run", "build", "--", "--outDir", str(destination), "--emptyOutDir"],
        cwd=ROOT / "frontend",
        env=env,
        check=True,
    )
    (destination / ".nojekyll").touch()
    print(
        f"Historical replay built at {destination}. No model server or credentials are included."
    )


if __name__ == "__main__":
    main()
