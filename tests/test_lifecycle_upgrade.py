"""Foreground lifecycle: no real application/model/launchd/UI operations.

The one POSIX process-tree test starts only disposable Python sentinels and an
unrelated ephemeral listener; it never touches ReviewRadar's service ports.
"""

import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

import pytest

SPEC = importlib.util.spec_from_file_location(
    "reviewradar_foreground_lifecycle",
    Path(__file__).resolve().parents[1] / "scripts/local_services.py",
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class Child:
    def __init__(self, pid, result=None):
        self.pid, self.result = pid, result
        self.waited = []

    def poll(self):
        return self.result

    def wait(self, timeout):
        self.waited.append(timeout)
        return 0


@pytest.fixture
def manager(tmp_path, monkeypatch):
    manager = module.LocalServices(tmp_path / "project with spaces", uid=987)
    monkeypatch.setattr(manager, "validate", lambda config: None)
    monkeypatch.setattr(manager, "inspect", lambda service: None)
    monkeypatch.setattr(manager, "port_free", lambda service: True)
    monkeypatch.setattr(module.signal, "signal", lambda number, handler: signal.SIG_DFL)
    return manager


def configuration(tmp_path):
    return {
        "runtime": str(tmp_path / "llama server"),
        "model": str(tmp_path / "model.gguf"),
    }


@pytest.mark.parametrize("blocked", ["owned_job", "occupied_port"])
def test_foreground_preflight_refuses_takeover_before_writes_or_children(
    manager, tmp_path, monkeypatch, blocked
):
    if blocked == "owned_job":
        monkeypatch.setattr(
            manager, "inspect", lambda service: {"pid": 91, "state": "running"}
        )
    else:
        monkeypatch.setattr(manager, "port_free", lambda service: service != "app")

    def forbidden(*args, **kwargs):
        raise AssertionError("Failed preflight must not write or create a process")

    monkeypatch.setattr(manager, "write_configuration", forbidden)
    monkeypatch.setattr(module.subprocess, "Popen", forbidden)
    with pytest.raises(module.ServiceError, match="still loaded|occupied"):
        manager.foreground(configuration(tmp_path), 5)
    assert not manager.directory.exists()


def test_foreground_uses_owned_groups_explicit_environment_and_terminal_lifetime(
    manager, tmp_path, monkeypatch, capsys
):
    monkeypatch.setenv("GH_TOKEN", "PRIVATE_TOKEN_DO_NOT_COPY")
    monkeypatch.setenv("RR_MODEL_KEY_FILE", "/some-other-project/key")
    monkeypatch.setenv("HTTP_PROXY", "http://secret@untrusted.invalid")
    calls = []
    children = [Child(41001), Child(41002)]

    def spawn(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return children[len(calls) - 1]

    monkeypatch.setattr(module.subprocess, "Popen", spawn)
    monkeypatch.setattr(manager, "wait_foreground", lambda *args: None)

    def stop_after_ready(owned):
        if len(owned) == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(manager, "check_foreground_children", stop_after_ready)
    cleaned = []
    monkeypatch.setattr(
        manager, "stop_foreground_children", lambda owned: cleaned.append(dict(owned))
    )
    config = configuration(tmp_path)
    result = manager.foreground(config, 5)
    assert result == {"foreground": "stopped", "saved_data": "preserved"}
    assert list(cleaned[0]) == ["model", "app"]
    assert calls[0][0][2:6] == [
        "--runtime",
        config["runtime"],
        "--model",
        config["model"],
    ]
    assert calls[1][0][-2:] == ["-m", "reviewradar"]
    for _, options in calls:
        assert options["start_new_session"] is True
        assert options["cwd"] == manager.root
        assert options["stderr"] == subprocess.STDOUT
        assert options["stdout"].closed
        assert "GH_TOKEN" not in options["env"]
        assert "HTTP_PROXY" not in options["env"]
    assert calls[1][1]["env"]["RR_MODEL_KEY_FILE"] == str(
        manager.root / ".runtime/model.key"
    )
    assert "PRIVATE_TOKEN_DO_NOT_COPY" not in capsys.readouterr().out
    assert manager.directory.stat().st_mode & 0o777 == 0o700
    for path in manager.directory.glob("foreground-*.log"):
        assert path.stat().st_mode & 0o777 == 0o600


def test_app_spawn_failure_cleans_already_started_model(manager, tmp_path, monkeypatch):
    model = Child(41001)
    calls = []

    def spawn(*args, **kwargs):
        calls.append(args)
        if len(calls) == 2:
            raise OSError("Cannot spawn app")
        return model

    monkeypatch.setattr(module.subprocess, "Popen", spawn)
    monkeypatch.setattr(manager, "wait_foreground", lambda *args: None)
    cleaned = []
    monkeypatch.setattr(
        manager, "stop_foreground_children", lambda owned: cleaned.append(dict(owned))
    )
    with pytest.raises(OSError, match="Cannot spawn app"):
        manager.foreground(configuration(tmp_path), 5)
    assert cleaned == [{"model": model}]


def test_model_exit_during_startup_never_starts_app(manager, tmp_path, monkeypatch):
    model = Child(41001, result=7)
    calls = []
    monkeypatch.setattr(
        module.subprocess, "Popen", lambda *args, **kwargs: calls.append(args) or model
    )
    monkeypatch.setattr(manager, "healthy", lambda service: True)
    cleaned = []
    monkeypatch.setattr(
        manager, "stop_foreground_children", lambda owned: cleaned.append(dict(owned))
    )
    with pytest.raises(module.ServiceError, match="model process exited"):
        manager.foreground(configuration(tmp_path), 5)
    assert len(calls) == 1
    assert cleaned == [{"model": model}]


def test_model_exit_while_app_waits_is_not_reported_ready(manager, monkeypatch):
    children = {"model": Child(41001, result=2), "app": Child(41002)}
    monkeypatch.setattr(manager, "healthy", lambda service: True)
    with pytest.raises(module.ServiceError, match="model process exited"):
        manager.wait_foreground("app", children, 5)


def test_readiness_timeout_fails_with_private_log_help(manager, monkeypatch):
    moments = iter([0, 0, 6])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(moments))
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    monkeypatch.setattr(manager, "healthy", lambda service: False)
    with pytest.raises(module.ServiceError, match="foreground-model.log"):
        manager.wait_foreground("model", {"model": Child(41001)}, 5)


def test_group_cleanup_terminates_only_live_invocation_groups(monkeypatch):
    children = {"model": Child(41001), "app": Child(41002)}
    active = {41001, 41002}
    calls = []

    def send(group, number):
        calls.append((group, number))
        if group not in active:
            raise ProcessLookupError
        if number == signal.SIGTERM:
            active.remove(group)

    monkeypatch.setattr(module.os, "killpg", send)
    module.LocalServices.stop_foreground_children(children)
    assert [(group, number) for group, number in calls if number] == [
        (41002, signal.SIGTERM),
        (41001, signal.SIGTERM),
    ]
    assert {group for group, _ in calls} == {41001, 41002}
    assert children["model"].waited == [3]
    assert children["app"].waited == [3]


def test_group_cleanup_escalates_after_bound_without_scanning_other_processes(
    monkeypatch,
):
    child = Child(41001)
    calls = []
    monkeypatch.setattr(
        module.os, "killpg", lambda group, number: calls.append((group, number))
    )
    moments = iter([0, 9])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(moments))
    module.LocalServices.stop_foreground_children({"model": child})
    assert calls == [(41001, signal.SIGTERM), (41001, 0), (41001, signal.SIGKILL)]
    assert child.waited == [3]


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group lifecycle")
def test_cleanup_stops_real_owned_descendant_and_keeps_unrelated_listener(tmp_path):
    # Disposable sentinels only. A runtime descendant opens an ephemeral port;
    # its wrapper waits/reaps it on TERM, matching the ownership problem that
    # terminating only the Python model wrapper would leave behind.
    receipt = tmp_path / "sentinel.json"
    descendant = """import json,os,socket,sys,time
from pathlib import Path
s=socket.socket();s.bind(('127.0.0.1',0));s.listen(1)
Path(sys.argv[1]).write_text(json.dumps({'pid':os.getpid(),'port':s.getsockname()[1]}))
time.sleep(60)
"""
    wrapper = """import signal,subprocess,sys,time
child=subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]])
def stop(number,frame):
    child.wait(timeout=3)
    sys.exit(0)
signal.signal(signal.SIGTERM,stop)
time.sleep(60)
"""
    child = subprocess.Popen(
        [sys.executable, "-c", wrapper, descendant, str(receipt)],
        start_new_session=True,
    )
    with socket.socket() as unrelated:
        unrelated.bind(("127.0.0.1", 0))
        unrelated.listen(1)
        unrelated_port = unrelated.getsockname()[1]
        try:
            deadline = time.monotonic() + 5
            while not receipt.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            data = json.loads(receipt.read_text())
            with socket.create_connection(("127.0.0.1", data["port"]), timeout=1):
                pass
            module.LocalServices.stop_foreground_children({"model": child})
            assert child.poll() is not None
            with pytest.raises(OSError):
                socket.create_connection(("127.0.0.1", data["port"]), timeout=0.2)
            with socket.create_connection(("127.0.0.1", unrelated_port), timeout=1):
                pass
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=3)


def test_foreground_cli_dispatch_does_not_load_launchd_jobs(
    manager, tmp_path, monkeypatch, capsys
):
    config = configuration(tmp_path)
    manager.write_configuration(config)
    invoked = []
    monkeypatch.setattr(
        manager,
        "foreground",
        lambda value, timeout: invoked.append((value, timeout))
        or {"foreground": "stopped"},
    )
    monkeypatch.setattr(
        manager,
        "start",
        lambda *args: pytest.fail("Foreground must not bootstrap launchd"),
    )
    monkeypatch.setattr(module, "LocalServices", lambda: manager)
    monkeypatch.setattr(module.sys, "platform", "darwin")
    monkeypatch.setattr(
        module.sys, "argv", ["local_services.py", "foreground", "--timeout", "5"]
    )
    assert module.main() == 0
    assert invoked == [(config, 5)]
    assert json.loads(capsys.readouterr().out) == {"foreground": "stopped"}


def test_signal_during_spawn_is_deferred_until_child_registered(
    manager, tmp_path, monkeypatch
):
    handlers = {}

    def register(number, handler):
        handlers[number] = handler
        return signal.SIG_DFL

    monkeypatch.setattr(module.signal, "signal", register)
    model = Child(41001)
    started = []

    def spawn(*args, **kwargs):
        started.append("model")
        handlers[signal.SIGTERM](signal.SIGTERM, None)
        return model

    monkeypatch.setattr(module.subprocess, "Popen", spawn)
    monkeypatch.setattr(manager, "healthy", lambda service: True)
    cleaned = []
    monkeypatch.setattr(
        manager, "stop_foreground_children", lambda owned: cleaned.append(dict(owned))
    )
    assert manager.foreground(configuration(tmp_path), 5)["foreground"] == "stopped"
    assert started == ["model"]
    assert cleaned == [{"model": model}]


def test_status_separates_endpoint_readiness_from_legacy_job_ownership(
    monkeypatch, tmp_path
):
    manager = module.LocalServices(tmp_path, uid=987)
    monkeypatch.setattr(manager, "inspect", lambda _service: None)
    monkeypatch.setattr(manager, "healthy", lambda _service: True)
    status = manager.status()
    assert status["endpoint_health"] == {"app": True, "model": True}
    assert all(not item["managed"] for item in status["services"].values())
    assert "legacy launchd" in status["status_scope"]
