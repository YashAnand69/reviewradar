"""Offline setup failures must be actionable and must not execute model files."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "rr_doctor", Path(__file__).parents[1] / "scripts/doctor.py"
)
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


def ready_root(tmp_path):
    (tmp_path / ".venv/bin").mkdir(parents=True)
    python = tmp_path / ".venv/bin/python"
    python.write_text("")
    python.chmod(0o700)
    (tmp_path / "requirements-lock.txt").write_text("fastapi==1.0\n")
    (tmp_path / "backend/reviewradar").mkdir(parents=True)
    (tmp_path / "backend/reviewradar/__main__.py").write_text("")
    dist = tmp_path / "frontend/dist"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text('<script src="./app.js"></script>')
    (dist / "app.js").write_text("")
    return tmp_path


def test_missing_install_does_not_execute_commands(tmp_path):
    with (
        patch.object(doctor.shutil, "which", return_value=None),
        patch.object(doctor, "command") as command,
    ):
        result = doctor.inspect(tmp_path)
    assert not result["source_reading_ready"]
    assert result["read_only"]
    command.assert_not_called()


def test_built_reading_needs_no_node_model_or_github(tmp_path):
    root = ready_root(tmp_path)
    with (
        patch.object(doctor.shutil, "which", return_value=None),
        patch.object(
            doctor,
            "command",
            return_value=json.dumps({"python": [3, 12], "mismatches": []}),
        ),
    ):
        result = doctor.inspect(root)
    assert result["source_reading_ready"]
    assert not result["inference_artifacts_verified"]
    assert str(root) not in json.dumps(result)


def test_missing_asset_and_wrong_dependencies_fail(tmp_path):
    root = ready_root(tmp_path)
    (root / "frontend/dist/app.js").unlink()
    with (
        patch.object(doctor.shutil, "which", return_value=None),
        patch.object(
            doctor,
            "command",
            return_value=json.dumps({"python": [3, 12], "mismatches": ["fastapi"]}),
        ),
    ):
        result = doctor.inspect(root)
    assert not result["source_reading_ready"]
    assert result["checks"][0]["status"] == "repair"


def test_model_files_are_never_executed_and_mismatch_is_reported(tmp_path):
    root = ready_root(tmp_path)
    (root / ".runtime/services").mkdir(parents=True)
    model = root / "weights"
    model.write_bytes(b"abc")
    runtime = root / "runtime"
    runtime.write_bytes(b"runtime")
    runtime.chmod(0o700)
    (root / ".runtime/services/config.json").write_text(
        json.dumps({"model": str(model), "runtime": str(runtime)})
    )
    (root / "model-manifest.json").write_text(
        json.dumps(
            {
                "model_bytes": 3,
                "model_sha256": "incorrect",
                "runtime_verified_binary_sha256": "incorrect",
            }
        )
    )
    with (
        patch.object(doctor.shutil, "which", return_value=None),
        patch.object(
            doctor,
            "command",
            return_value=json.dumps({"python": [3, 12], "mismatches": []}),
        ) as command,
    ):
        result = doctor.inspect(root, verify_artifacts=True)
    assert result["source_reading_ready"]
    assert result["checks"][-1]["status"] == "repair"
    assert all(str(runtime) not in str(call) for call in command.call_args_list)
    assert str(model) not in json.dumps(result)
