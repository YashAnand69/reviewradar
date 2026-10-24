#!/usr/bin/env python3
"""Run ReviewRadar in a dedicated Terminal or manage its legacy launchd jobs.

The foreground action owns only new child groups and remains attached to a
visible Terminal; Ctrl+C requests bounded cleanup. It creates no launchd job or
login item. Start independently from Finder/Terminal; actual ChatGPT-quit
survival still requires a user lifecycle check. Legacy jobs remain supported,
but macOS can remove jobs attributed to ChatGPT when that app quits.
No download, credential copying, process takeover, or login startup is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import signal
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
PORTS = {"app": 8893, "model": 18085}


class ServiceError(RuntimeError):
    pass


class LocalServices:
    def __init__(self, root: Path = ROOT, uid: int | None = None):
        self.root = root.resolve()
        self.uid = os.getuid() if uid is None else uid
        self.domain = f"gui/{self.uid}"
        suffix = hashlib.sha256(str(self.root).encode()).hexdigest()[:16]
        self.prefix = f"local.reviewradar.{self.uid}.{suffix}"
        self.directory = self.root / ".runtime/services"
        self.config_file = self.directory / "config.json"

    def label(self, service: str) -> str:
        if service not in PORTS:
            raise ValueError("Unknown ReviewRadar service")
        return f"{self.prefix}.{service}"

    def plist_path(self, service: str) -> Path:
        return self.directory / f"{self.label(service)}.plist"

    def target(self, service: str) -> str:
        return f"{self.domain}/{self.label(service)}"

    def launchctl(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["/bin/launchctl", *arguments],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def inspect(self, service: str) -> dict | None:
        result = self.launchctl("print", self.target(service))
        if result.returncode:
            # Do not mistake a permission or unavailable-session failure for an
            # absent job, then bootstrap into an unknown state.
            if "Could not find service" in result.stderr:
                return None
            raise ServiceError(
                "Cannot inspect the current macOS login service. "
                "Run this from your signed-in desktop session."
            )
        match = re.search(r"^\s*path = (.+)$", result.stdout, re.MULTILINE)
        if not match or Path(match.group(1)).resolve() != self.plist_path(service):
            raise ServiceError(
                f"The {service} service label is not owned by this project; no change made."
            )
        state = re.search(r"^\s*state = (.+)$", result.stdout, re.MULTILINE)
        pid = re.search(r"^\s*pid = (\d+)$", result.stdout, re.MULTILINE)
        return {
            "state": state.group(1) if state else "unknown",
            "pid": int(pid.group(1)) if pid else None,
        }

    def load_config(self) -> dict:
        try:
            data = json.loads(self.config_file.read_text())
        except (OSError, ValueError) as error:
            raise ServiceError(
                "No valid saved service configuration. Start with explicit --runtime and --model paths."
            ) from error
        if (
            not isinstance(data, dict)
            or set(data) != {"runtime", "model"}
            or any(not isinstance(value, str) or not value for value in data.values())
        ):
            raise ServiceError("Saved service configuration has unexpected fields.")
        return data

    def configuration(self, runtime: Path | None, model: Path | None) -> dict:
        saved = self.load_config() if runtime is None or model is None else {}
        return {
            "runtime": str((runtime or Path(saved["runtime"])).expanduser().resolve()),
            "model": str((model or Path(saved["model"])).expanduser().resolve()),
        }

    def validate(self, config: dict) -> None:
        files = {
            "Python environment": self.root / ".venv/bin/python",
            "Runtime": Path(config["runtime"]),
            "Model": Path(config["model"]),
            "Model launcher": self.root / "scripts/run_model.py",
            "Frontend build": self.root / "frontend/dist/index.html",
        }
        for description, path in files.items():
            if not path.is_file():
                raise ServiceError(f"{description} is missing: {path}")
        for name in ("Python environment", "Runtime"):
            if not os.access(files[name], os.X_OK):
                raise ServiceError(f"{name} is not executable: {files[name]}")

    def build_plist(self, service: str, config: dict) -> dict:
        python = str(self.root / ".venv/bin/python")
        environment = {
            "HOME": str(Path.home()),
            "PATH": ":".join(
                dict.fromkeys(
                    [
                        str(self.root / ".venv/bin"),
                        str(Path(shutil.which("gh")).parent)
                        if shutil.which("gh")
                        else "/usr/local/bin",
                        "/opt/homebrew/bin",
                        "/usr/local/bin",
                        "/usr/bin",
                        "/bin",
                    ]
                )
            ),
            "PYTHONUNBUFFERED": "1",
        }
        if service == "app":
            arguments = [python, "-m", "reviewradar"]
            environment.update(
                {
                    "PYTHONPATH": str(self.root / "backend"),
                    "RR_PORT": str(PORTS["app"]),
                    "RR_MODEL_URL": f"http://127.0.0.1:{PORTS['model']}",
                    "RR_MODEL_KEY_FILE": str(self.root / ".runtime/model.key"),
                    "RR_DATA_DIR": str(self.root / ".data"),
                }
            )
        else:
            arguments = [
                python,
                str(self.root / "scripts/run_model.py"),
                "--runtime",
                config["runtime"],
                "--model",
                config["model"],
                "--port",
                str(PORTS["model"]),
            ]
        return {
            "Label": self.label(service),
            "ProgramArguments": arguments,
            "WorkingDirectory": str(self.root),
            "EnvironmentVariables": environment,
            "RunAtLoad": True,
            "KeepAlive": True,
            "ThrottleInterval": 30,
            "ExitTimeOut": 15,
            "AbandonProcessGroup": False,
            "StandardOutPath": str(self.directory / f"{service}.log"),
            "StandardErrorPath": str(self.directory / f"{service}.error.log"),
        }

    def write_configuration(self, config: dict) -> None:
        self.directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        self.directory.chmod(0o700)
        for service in PORTS:
            self.plist_path(service).write_bytes(
                plistlib.dumps(self.build_plist(service, config))
            )
            self.plist_path(service).chmod(0o600)
        self.config_file.write_text(json.dumps(config, indent=2) + "\n")
        self.config_file.chmod(0o600)

    @staticmethod
    def port_free(service: str) -> bool:
        with socket.socket() as probe:
            try:
                # Match a real server restart: completed connections may remain
                # in TIME_WAIT after stop. listen() still rejects an active
                # listener, including one which also uses SO_REUSEADDR.
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind(("127.0.0.1", PORTS[service]))
                probe.listen(1)
            except OSError:
                return False
        return True

    @staticmethod
    def healthy(service: str) -> bool:
        endpoint = "/api/health" if service == "app" else "/health"
        # Local requests must never go through an inherited HTTP proxy.
        opener = build_opener(ProxyHandler({}))
        try:
            with opener.open(
                f"http://127.0.0.1:{PORTS[service]}{endpoint}", timeout=2
            ) as response:
                data = json.loads(response.read(8192))
                if service == "app":
                    return data.get("status") == "ok" and data.get("mode") == "local"
                return data.get("status") == "ok"
        except (OSError, ValueError, URLError, AttributeError):
            return False

    def wait_healthy(self, service: str, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.inspect(service)
            if job is None:
                raise ServiceError(
                    f"The {service} service disappeared during startup. "
                    "Run status and retry start after shutdown has finished."
                )
            if (
                job
                and job["state"] == "running"
                and job["pid"]
                and self.healthy(service)
            ):
                return
            time.sleep(1)
        raise ServiceError(
            f"The {service} service did not become ready. Inspect {self.directory / (service + '.error.log')} "
            f"and {self.directory / (service + '.log')}."
        )

    def start(self, config: dict, timeout: float) -> dict:
        self.validate(config)
        existing = {service: self.inspect(service) for service in PORTS}
        if any(existing.values()) and self.load_config() != config:
            raise ServiceError(
                "Stop this project's services before changing its model/runtime paths."
            )
        for service in PORTS:
            if existing[service] is None and not self.port_free(service):
                raise ServiceError(
                    f"Port {PORTS[service]} is occupied by an unmanaged process. "
                    "No process was stopped. Stop that process yourself if appropriate, then retry."
                )
        self.write_configuration(config)
        added = []
        try:
            for service in ("model", "app"):
                if existing[service] is None:
                    result = self.launchctl(
                        "bootstrap", self.domain, str(self.plist_path(service))
                    )
                    if result.returncode:
                        raise ServiceError(
                            f"macOS could not start the {service} service (exit {result.returncode}). "
                            "No login-startup item was installed."
                        )
                    added.append(service)
                self.wait_healthy(service, timeout)
        except (ServiceError, OSError, subprocess.TimeoutExpired):
            # Roll back this invocation only; never stop a pre-existing service.
            for service in reversed(added):
                self.stop_service(service)
            raise
        return self.status()

    def foreground(self, config: dict, timeout: float) -> dict:
        """Own app/model children in a visible Terminal session, without launchd.

        Run this independently from Finder/Terminal. This process remains the
        supervisor; closing its Terminal or Ctrl+C requests cleanup. There is no
        PID-file takeover, detached daemon, login item, or automatic restart.
        """
        self.validate(config)
        # Check every owner and listener before configuration writes or children.
        for service in PORTS:
            if self.inspect(service) is not None:
                raise ServiceError(
                    "Owned login-session jobs are still loaded. Stop them before "
                    "starting the foreground session. No process was changed."
                )
        for service in PORTS:
            if not self.port_free(service):
                raise ServiceError(
                    f"Port {PORTS[service]} is occupied. A foreground session or "
                    "another application may already be running. Return to its "
                    "Terminal and stop it if appropriate; no process was stopped."
                )
        self.write_configuration(config)
        children: dict[str, subprocess.Popen] = {}
        logs = []
        previous_handlers = {}
        self._foreground_stop_requested = False

        def interrupted(signum, frame):
            # Defer the interruption until Popen's returned child has been
            # registered. Raising inside process creation can orphan a new group.
            self._foreground_stop_requested = True

        try:
            for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                previous_handlers[signum] = signal.signal(signum, interrupted)
            for service in ("model", "app"):
                self.check_foreground_children(children)
                log_path = self.directory / f"foreground-{service}.log"
                descriptor = os.open(
                    log_path,
                    os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW,
                    0o600,
                )
                os.fchmod(descriptor, 0o600)
                log = os.fdopen(descriptor, "a")
                logs.append(log)
                specification = self.build_plist(service, config)
                children[service] = subprocess.Popen(
                    specification["ProgramArguments"],
                    cwd=self.root,
                    env=specification["EnvironmentVariables"],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    # Each invocation owns only these new groups, including the
                    # llama-server descendant of the verified model launcher.
                    start_new_session=True,
                )
                self.wait_foreground(service, children, timeout)
            print(
                json.dumps(
                    {
                        "foreground": "ready",
                        "url": "http://127.0.0.1:8893/",
                        "supervisor_pid": os.getpid(),
                        "supervisor_parent_pid": os.getppid(),
                        "children": {
                            name: child.pid for name, child in children.items()
                        },
                        "lifetime": "Keep this dedicated Terminal open; Ctrl+C stops this session. No automatic restart or login startup.",
                        "quit_test": "ChatGPT-quit survival requires an actual independent launch and quit test; readiness alone does not verify it.",
                        "log_directory": str(self.directory),
                    },
                    indent=2,
                ),
                flush=True,
            )
            while True:
                self.check_foreground_children(children)
                time.sleep(0.5)
        except KeyboardInterrupt:
            return {"foreground": "stopped", "saved_data": "preserved"}
        finally:
            # Ignore a second Ctrl+C while the bounded cleanup finishes.
            for signum in previous_handlers:
                signal.signal(signum, signal.SIG_IGN)
            try:
                self.stop_foreground_children(children)
            finally:
                for log in logs:
                    log.close()
                for signum, handler in previous_handlers.items():
                    signal.signal(signum, handler)

    def check_foreground_children(self, children: dict[str, subprocess.Popen]) -> None:
        if getattr(self, "_foreground_stop_requested", False):
            raise KeyboardInterrupt
        for service, child in children.items():
            result = child.poll()
            if result is not None:
                raise ServiceError(
                    f"The foreground {service} process exited (status {result}). "
                    f"Inspect {self.directory / ('foreground-' + service + '.log')}. "
                    "This session's other child processes will be stopped. "
                    "No unrelated process will be changed."
                )

    def wait_foreground(
        self, service: str, children: dict[str, subprocess.Popen], timeout: float
    ) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.check_foreground_children(children)
            if self.healthy(service):
                return
            time.sleep(0.2)
        raise ServiceError(
            f"The foreground {service} process did not become ready. "
            f"Inspect {self.directory / ('foreground-' + service + '.log')}."
        )

    @staticmethod
    def stop_foreground_children(children: dict[str, subprocess.Popen]) -> None:
        """Terminate only new process groups retained by this live invocation.

        No persisted/stale PID is accepted. A launcher which has exited can
        still have a runtime descendant in its original group, so stop groups
        rather than just the immediate Python wrapper.
        """
        groups = [child.pid for child in reversed(list(children.values()))]

        def send(group: int, signum: int) -> bool:
            try:
                os.killpg(group, signum)
                return True
            except ProcessLookupError:
                return False

        for group in groups:
            send(group, signal.SIGTERM)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            for child in children.values():
                child.poll()  # Reap wrapper children while descendants exit.
            if not any(send(group, 0) for group in groups):
                break
            time.sleep(0.1)
        for group in groups:
            if send(group, 0):
                send(group, signal.SIGKILL)
        for child in children.values():
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Bounded cleanup already requested KILL for this exact group.
                # Never scan or kill a process chosen by name/occupied port.
                pass

    def stop_service(self, service: str) -> None:
        if self.inspect(service) is None:
            return
        result = self.launchctl("bootout", self.target(service))
        if result.returncode:
            raise ServiceError(
                f"macOS could not stop this project's {service} service."
            )
        # bootout requests teardown, but the old job can remain observable
        # briefly. Returning early lets the next start mistake that dying job
        # for an existing service and omit its bootstrap altogether.
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if self.inspect(service) is None and self.port_free(service):
                return
            time.sleep(0.2)
        raise ServiceError(
            f"The {service} service has not fully stopped. "
            "Run status before retrying; no other process was stopped."
        )

    def stop(self) -> dict:
        # Inspect both before any mutation: an ownership conflict changes nothing.
        for service in PORTS:
            self.inspect(service)
        for service in ("app", "model"):
            self.stop_service(service)
        return self.status()

    def status(self) -> dict:
        result = {
            "url": "http://127.0.0.1:8893/",
            "lifetime": "Legacy launchd jobs only; foreground sessions are controlled by their own Terminal. ChatGPT-quit survival requires an actual test.",
            "status_scope": "Job state and managed fields refer only to legacy launchd jobs. Endpoint health does not prove process ownership.",
            "endpoint_health": {service: self.healthy(service) for service in PORTS},
            "services": {},
        }
        for service in PORTS:
            job = self.inspect(service)
            result["services"][service] = {
                "managed": job is not None,
                "state": job["state"] if job else "not loaded",
                "pid": job["pid"] if job else None,
                "healthy": self.healthy(service)
                if job and job["state"] == "running" and job["pid"]
                else False,
                "log": str(self.directory / f"{service}.log"),
                "error_log": str(self.directory / f"{service}.error.log"),
            }
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("start", "status", "stop", "check", "foreground")
    )
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument(
        "--timeout",
        type=float,
        default=180,
        help="Readiness wait per service, seconds (5–600).",
    )
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error(
            "This local service controller requires macOS; use the documented foreground launchers elsewhere."
        )
    if not 5 <= args.timeout <= 600:
        parser.error("Timeout must be between 5 and 600 seconds.")
    services = LocalServices()
    try:
        if args.action == "check":
            configuration = services.configuration(args.runtime, args.model)
            services.validate(configuration)
            result = {
                "configuration": "valid paths and executable prerequisites",
                "services_changed": False,
                "note": "Artifact checksums are verified during model startup, not by this preflight.",
            }
        elif args.action == "foreground":
            result = services.foreground(
                services.configuration(args.runtime, args.model), args.timeout
            )
        elif args.action == "start":
            result = services.start(
                services.configuration(args.runtime, args.model), args.timeout
            )
        elif args.action == "stop":
            result = services.stop()
        else:
            result = services.status()
        print(json.dumps(result, indent=2))
        return 0
    except (ServiceError, OSError, subprocess.TimeoutExpired) as error:
        print(f"ReviewRadar services: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
