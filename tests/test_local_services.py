"""Lifecycle safety checks with fake launchd: never installs or stops real jobs."""

import importlib.util
import json
from pathlib import Path
import plistlib
import socket
import subprocess
import sys

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/local_services.py"
SPEC = importlib.util.spec_from_file_location("reviewradar_local_services", MODULE_PATH)
services = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = services
SPEC.loader.exec_module(services)
MODEL_SPEC = importlib.util.spec_from_file_location(
    "reviewradar_run_model", MODULE_PATH.with_name("run_model.py")
)
model_launcher = importlib.util.module_from_spec(MODEL_SPEC)
MODEL_SPEC.loader.exec_module(model_launcher)


@pytest.fixture(params=["services", "model"])
def port_available(request, monkeypatch):
    def check(port):
        if request.param == "model":
            return model_launcher.port_available(port)
        monkeypatch.setitem(services.PORTS, "app", port)
        return services.LocalServices.port_free("app")

    return check


@pytest.mark.parametrize("reuse", [False, True])
def test_port_probe_refuses_real_unmanaged_listener(port_available, reuse):
    # Ephemeral test ports only: this does not contact any project service.
    with socket.socket() as listener:
        if reuse:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        assert port_available(listener.getsockname()[1]) is False


def test_port_probe_allows_immediate_restart_after_accepted_connection(port_available):
    with socket.socket() as listener, socket.socket() as client:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        listener.listen(1)
        client.settimeout(2)
        client.connect(("127.0.0.1", port))
        accepted, _ = listener.accept()
        # Active close on the server leaves its completed connection in
        # TIME_WAIT. Waiting for EOF makes the test independent of timing.
        accepted.close()
        assert client.recv(1) == b""
    assert port_available(port) is True


@pytest.fixture
def manager(tmp_path, monkeypatch):
    manager = services.LocalServices(tmp_path / "project with spaces", uid=987)
    monkeypatch.setattr(manager, "validate", lambda config: None)
    return manager


def config(tmp_path):
    return {
        "runtime": str(tmp_path / "llama server"),
        "model": str(tmp_path / "gemma model.gguf"),
    }


def test_jobs_are_project_scoped_and_do_not_install_at_login(manager, tmp_path):
    other = services.LocalServices(tmp_path / "another project", uid=987)
    assert manager.label("app") != other.label("app")
    assert manager.target("model").startswith("gui/987/local.reviewradar.987.")
    assert manager.plist_path("app").parent == manager.root / ".runtime/services"
    assert "Library/LaunchAgents" not in str(manager.plist_path("app"))


def test_plists_pass_paths_as_arguments_and_never_inherit_credentials(
    manager, tmp_path, monkeypatch
):
    monkeypatch.setenv("GH_TOKEN", "DO-NOT-COPY")
    monkeypatch.setenv("HTTP_PROXY", "http://credential:secret@proxy.invalid")
    configuration = config(tmp_path)
    model = manager.build_plist("model", configuration)
    app = manager.build_plist("app", configuration)
    assert model["ProgramArguments"][2:6] == [
        "--runtime",
        configuration["runtime"],
        "--model",
        configuration["model"],
    ]
    assert model["ProgramArguments"][-2:] == ["--port", "18085"]
    assert app["ProgramArguments"][-2:] == ["-m", "reviewradar"]
    assert app["EnvironmentVariables"]["RR_MODEL_URL"] == "http://127.0.0.1:18085"
    assert app["EnvironmentVariables"]["RR_PORT"] == "8893"
    assert "DO-NOT-COPY" not in json.dumps([app, model])
    assert "secret@" not in json.dumps([app, model])
    assert app["KeepAlive"] and not app["AbandonProcessGroup"]
    assert app["WorkingDirectory"] == str(manager.root)


def test_configuration_files_are_private_and_contain_no_key(manager, tmp_path):
    configuration = config(tmp_path)
    manager.write_configuration(configuration)
    assert manager.load_config() == configuration
    assert manager.directory.stat().st_mode & 0o777 == 0o700
    assert manager.config_file.stat().st_mode & 0o777 == 0o600
    saved = plistlib.loads(manager.plist_path("model").read_bytes())
    assert saved["Label"] == manager.label("model")
    assert "api-key" not in json.dumps(saved)


def test_inspect_refuses_same_label_from_different_path(manager, monkeypatch):
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: subprocess.CompletedProcess(
            args, 0, "path = /tmp/not-ours.plist\nstate = running\npid = 42\n", ""
        ),
    )
    with pytest.raises(services.ServiceError, match="not owned"):
        manager.inspect("app")


def test_inspect_distinguishes_unavailable_session_from_absent_job(
    manager, monkeypatch
):
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: subprocess.CompletedProcess(
            args, 1, "", "Operation not permitted"
        ),
    )
    with pytest.raises(services.ServiceError, match="Cannot inspect"):
        manager.inspect("app")
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: subprocess.CompletedProcess(
            args, 113, "", "Could not find service in domain"
        ),
    )
    assert manager.inspect("app") is None


def test_unmanaged_port_blocks_start_without_any_writes_or_bootstrap(
    manager, tmp_path, monkeypatch
):
    calls = []
    monkeypatch.setattr(manager, "inspect", lambda service: None)
    monkeypatch.setattr(manager, "port_free", lambda service: service != "app")
    monkeypatch.setattr(manager, "launchctl", lambda *args: calls.append(args))
    with pytest.raises(services.ServiceError, match="unmanaged"):
        manager.start(config(tmp_path), 5)
    assert calls == []
    assert not manager.directory.exists()


def test_failed_new_app_rolls_back_only_new_job(manager, tmp_path, monkeypatch):
    configuration = config(tmp_path)
    manager.write_configuration(configuration)
    monkeypatch.setattr(
        manager,
        "inspect",
        lambda service: {"state": "running", "pid": 42} if service == "model" else None,
    )
    monkeypatch.setattr(manager, "port_free", lambda service: True)
    calls = []
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: calls.append(args)
        or subprocess.CompletedProcess(args, 0, "", ""),
    )
    stopped = []
    monkeypatch.setattr(
        manager, "stop_service", lambda service: stopped.append(service)
    )

    def wait(service, timeout):
        if service == "app":
            raise services.ServiceError("not ready")

    monkeypatch.setattr(manager, "wait_healthy", wait)
    with pytest.raises(services.ServiceError, match="not ready"):
        manager.start(configuration, 5)
    assert calls == [("bootstrap", "gui/987", str(manager.plist_path("app")))]
    assert stopped == ["app"]


def test_changed_model_config_does_not_reconfigure_running_jobs(
    manager, tmp_path, monkeypatch
):
    manager.write_configuration(config(tmp_path))
    monkeypatch.setattr(
        manager, "inspect", lambda service: {"state": "running", "pid": 42}
    )
    with pytest.raises(services.ServiceError, match="Stop this project's services"):
        manager.start({"runtime": "/new/runtime", "model": "/new/model"}, 5)
    assert manager.load_config() == config(tmp_path)


def test_stop_checks_both_owners_before_any_bootout(manager, monkeypatch):
    def inspect(service):
        if service == "model":
            raise services.ServiceError("not owned")
        return {"state": "running", "pid": 42}

    monkeypatch.setattr(manager, "inspect", inspect)
    calls = []
    monkeypatch.setattr(manager, "launchctl", lambda *args: calls.append(args))
    with pytest.raises(services.ServiceError, match="not owned"):
        manager.stop()
    assert calls == []


def test_stop_targets_only_exact_owned_job(manager, monkeypatch):
    states = iter([{"state": "running", "pid": 42}, None])
    monkeypatch.setattr(manager, "inspect", lambda service: next(states))
    monkeypatch.setattr(manager, "port_free", lambda service: True)
    calls = []
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: calls.append(args)
        or subprocess.CompletedProcess(args, 0, "", ""),
    )
    manager.stop_service("app")
    assert calls == [("bootout", manager.target("app"))]


def test_stop_waits_for_async_unload_and_listener_exit(manager, monkeypatch):
    job = {"state": "running", "pid": 42}
    states = iter([job, job, None, None])
    ports = iter([False, True])
    sleeps = []
    monkeypatch.setattr(manager, "inspect", lambda service: next(states))
    monkeypatch.setattr(manager, "port_free", lambda service: next(ports))
    monkeypatch.setattr(services.time, "sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: subprocess.CompletedProcess(args, 0, "", ""),
    )
    manager.stop_service("app")
    # One wait for the dying launchd record, another for its listener.
    assert sleeps == [0.2, 0.2]


def test_stop_timeout_reports_incomplete_shutdown_without_other_actions(
    manager, monkeypatch
):
    monkeypatch.setattr(
        manager, "inspect", lambda service: {"state": "running", "pid": 42}
    )
    moments = iter([0, 31])
    monkeypatch.setattr(services.time, "monotonic", lambda: next(moments))
    calls = []
    monkeypatch.setattr(
        manager,
        "launchctl",
        lambda *args: calls.append(args)
        or subprocess.CompletedProcess(args, 0, "", ""),
    )
    with pytest.raises(services.ServiceError, match="has not fully stopped"):
        manager.stop_service("app")
    assert calls == [("bootout", manager.target("app"))]


def test_start_readiness_fails_promptly_if_registered_job_disappears(
    manager, monkeypatch
):
    monkeypatch.setattr(manager, "inspect", lambda service: None)
    with pytest.raises(services.ServiceError, match="disappeared during startup"):
        manager.wait_healthy("app", 180)


def test_validation_rejects_missing_frontend_before_start(manager, tmp_path):
    with pytest.raises(services.ServiceError, match="Python environment is missing"):
        services.LocalServices.validate(manager, config(tmp_path))


@pytest.mark.parametrize("explicit", [False, True])
def test_cli_check_validates_without_service_operations(
    manager, tmp_path, monkeypatch, capsys, explicit
):
    configuration = config(tmp_path)
    manager.write_configuration(configuration)
    before = {path.name: path.read_bytes() for path in manager.directory.iterdir()}
    validated = []
    monkeypatch.setattr(manager, "validate", lambda value: validated.append(value))

    def forbidden(*args, **kwargs):
        raise AssertionError(
            "Preflight must not inspect, start, stop or write services"
        )

    for name in (
        "launchctl",
        "start",
        "stop",
        "status",
        "inspect",
        "write_configuration",
    ):
        monkeypatch.setattr(manager, name, forbidden)
    monkeypatch.setattr(services, "LocalServices", lambda: manager)
    monkeypatch.setattr(services.sys, "platform", "darwin")
    arguments = ["local_services.py", "check"]
    if explicit:
        arguments += [
            "--runtime",
            configuration["runtime"],
            "--model",
            configuration["model"],
        ]
    monkeypatch.setattr(services.sys, "argv", arguments)
    assert services.main() == 0
    assert validated == [configuration]
    report = json.loads(capsys.readouterr().out)
    assert report["services_changed"] is False
    assert "not by this preflight" in report["note"]
    assert {
        path.name: path.read_bytes() for path in manager.directory.iterdir()
    } == before


@pytest.mark.parametrize(
    "saved", [None, "{invalid json", '{"runtime": "/only-runtime"}']
)
def test_cli_check_reports_missing_or_malformed_config_without_mutation(
    manager, monkeypatch, capsys, saved
):
    if saved is not None:
        manager.directory.mkdir(parents=True)
        manager.config_file.write_text(saved)

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid preflight must not change services")

    for name in (
        "launchctl",
        "start",
        "stop",
        "status",
        "inspect",
        "write_configuration",
    ):
        monkeypatch.setattr(manager, name, forbidden)
    monkeypatch.setattr(services, "LocalServices", lambda: manager)
    monkeypatch.setattr(services.sys, "platform", "darwin")
    monkeypatch.setattr(services.sys, "argv", ["local_services.py", "check"])
    assert services.main() == 1
    assert "ReviewRadar services:" in capsys.readouterr().err
    if saved is None:
        assert not manager.directory.exists()
    else:
        assert manager.config_file.read_text() == saved


def test_cli_check_reports_invalid_artifact_before_service_operations(
    manager, tmp_path, monkeypatch, capsys
):
    manager.write_configuration(config(tmp_path))

    def invalid_artifact(value):
        raise services.ServiceError("Model is missing")

    def forbidden(*args, **kwargs):
        raise AssertionError("Preflight must not change services")

    monkeypatch.setattr(manager, "validate", invalid_artifact)
    for name in (
        "launchctl",
        "start",
        "stop",
        "status",
        "inspect",
        "write_configuration",
    ):
        monkeypatch.setattr(manager, name, forbidden)
    monkeypatch.setattr(services, "LocalServices", lambda: manager)
    monkeypatch.setattr(services.sys, "platform", "darwin")
    monkeypatch.setattr(services.sys, "argv", ["local_services.py", "check"])
    assert services.main() == 1
    assert "Model is missing" in capsys.readouterr().err
