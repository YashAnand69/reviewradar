#!/usr/bin/env python3
"""Start an explicitly supplied llama.cpp runtime with the pinned model.

No automatic download, dependency installation, cloud call or process takeover.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def port_available(port: int) -> bool:
    """Allow a stopped server's TIME_WAIT sockets, never an active listener."""
    with socket.socket() as probe:
        try:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("127.0.0.1", port))
            probe.listen(1)
        except OSError:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime",
        required=True,
        type=Path,
        help="Path to the pinned llama-server build",
    )
    parser.add_argument(
        "--model", required=True, type=Path, help="Path to the pinned GGUF model"
    )
    parser.add_argument("--port", type=int, default=18085)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "model-manifest.json").read_text())
    runtime, model = (
        args.runtime.expanduser().resolve(),
        args.model.expanduser().resolve(),
    )
    if not runtime.is_file() or not os.access(runtime, os.X_OK) or not model.is_file():
        parser.error(
            "Runtime must be an executable file and model must be a readable file."
        )
    if not 1024 <= args.port <= 65535:
        parser.error("Port must be between 1024 and 65535.")
    if not port_available(args.port):
        parser.error(
            "The model port is occupied. Choose another port; no process was stopped."
        )
    print("Verifying the model artifact…", flush=True)
    if sha256_file(model) != manifest["model_sha256"]:
        parser.error(
            "Model checksum does not match model-manifest.json. No runtime was started."
        )
    version = subprocess.run(
        [str(runtime), "--version"], capture_output=True, text=True, timeout=15
    )
    known_binary = sha256_file(runtime) == manifest["runtime_verified_binary_sha256"]
    reported_commit = manifest["runtime_commit"][:7] in version.stdout + version.stderr
    if version.returncode or not (known_binary or reported_commit):
        parser.error(
            "Runtime must match the verified binary checksum or report the pinned source commit."
        )
    runtime_dir = ROOT / ".runtime"
    runtime_dir.mkdir(mode=0o700, exist_ok=True)
    key_path = runtime_dir / "model.key"
    if not key_path.exists():
        fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as key:
            key.write(secrets.token_urlsafe(36) + "\n")
    key_path.chmod(0o600)
    command = [
        str(runtime),
        "--model",
        str(model),
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
        "--ctx-size",
        str(manifest["context_tokens"]),
        "--parallel",
        "1",
        "--no-context-shift",
        "--api-key-file",
        str(key_path),
        "--alias",
        manifest["alias"],
        "--reasoning-budget",
        "0",
        "--chat-template-kwargs",
        '{"enable_thinking":false}',
        "--no-webui",
        "--offline",
    ]
    print(
        f"Starting verified local model on 127.0.0.1:{args.port}; Ctrl+C stops this process.",
        flush=True,
    )
    try:
        return subprocess.call(command, cwd=ROOT)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
