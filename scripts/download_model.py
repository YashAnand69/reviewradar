#!/usr/bin/env python3
"""Explicitly download and verify the manifest's GGUF artifact (~2.84 GB)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "model-manifest.json").read_text())
    directory = ROOT / ".model"
    directory.mkdir(exist_ok=True)
    target = directory / manifest["artifact"]
    if target.exists():
        raise SystemExit(
            "A model file already exists. Verify it or remove it deliberately before downloading again."
        )
    temporary = target.with_suffix(".download")
    if temporary.exists():
        raise SystemExit(
            "A previous partial download exists. Remove the .download file deliberately before retrying."
        )
    print(
        f"Downloading {manifest['model_bytes']:,} bytes from the pinned public artifact. No paid service is used."
    )
    digest = hashlib.sha256()
    written = 0
    try:
        request = urllib.request.Request(
            manifest["model_url"], headers={"User-Agent": "ReviewRadar-model-setup/0.1"}
        )
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            temporary.open("xb") as output,
        ):
            while chunk := response.read(4 * 1024 * 1024):
                written += len(chunk)
                if written > manifest["model_bytes"]:
                    raise ValueError("Artifact exceeds expected size")
                digest.update(chunk)
                output.write(chunk)
        if (
            written != manifest["model_bytes"]
            or digest.hexdigest() != manifest["model_sha256"]
        ):
            raise ValueError(
                "Artifact size/checksum did not match; partial file retained for inspection"
            )
        temporary.replace(target)
    except Exception as error:
        raise SystemExit(
            f"Download failed: {error}. A partial .download file may remain; it is never used as a model."
        ) from error
    print(f"Verified model saved to {target}")


if __name__ == "__main__":
    main()
