#!/usr/bin/env python3
"""Run the DeepSight backend and frontend development servers together."""

from __future__ import annotations

import argparse
import atexit
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parent
BACKEND_DIRECTORY = REPOSITORY_ROOT / "backend"
FRONTEND_DIRECTORY = REPOSITORY_ROOT / "frontend"
HOST = "127.0.0.1"
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 5173
STARTUP_TIMEOUT_SECONDS = 60


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the DeepSight backend and frontend on 127.0.0.1."
    )
    parser.add_argument("--backend-port", type=int, default=DEFAULT_BACKEND_PORT)
    parser.add_argument("--frontend-port", type=int, default=DEFAULT_FRONTEND_PORT)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--with-worker", action="store_true", help="Start a Celery video worker; Redis must already be ready.")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable backend auto-reload.",
    )
    return parser.parse_args()


def require_port_available(port: int) -> None:
    if not 1 <= port <= 65535:
        raise RuntimeError(f"Invalid port: {port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((HOST, port))
        except OSError as error:
            raise RuntimeError(f"Port {port} is already in use on {HOST}.") from error


def wait_for_url(
    url: str,
    process: subprocess.Popen[bytes],
    service_name: str,
    timeout: int = STARTUP_TIMEOUT_SECONDS,
) -> bytes:
    deadline = time.monotonic() + timeout
    last_error = "not ready"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"{service_name} exited during startup with code {process.returncode}."
            )
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return response.read()
        except (OSError, urllib.error.URLError) as error:
            last_error = error.__class__.__name__
        time.sleep(0.5)
    raise RuntimeError(
        f"{service_name} was not ready after {timeout} seconds ({last_error})."
    )


def process_options() -> dict[str, object]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def create_windows_job() -> Any | None:
    """Create a kill-on-close job so abrupt launcher exits cannot orphan children."""
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
        )]

    class BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimitInformation),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None
    information = ExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = 0x00002000
    configured = kernel32.SetInformationJobObject(
        job, 9, ctypes.byref(information), ctypes.sizeof(information)
    )
    if not configured:
        kernel32.CloseHandle(job)
        return None
    return job


def assign_to_windows_job(job: Any | None, process: subprocess.Popen[bytes]) -> None:
    if os.name == "nt" and job is not None:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        if not kernel32.AssignProcessToJobObject(job, int(process._handle)):  # type: ignore[attr-defined]
            raise RuntimeError("Could not attach a development server to the launcher job.")


def close_windows_job(job: Any | None) -> None:
    if os.name == "nt" and job is not None:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle(job)


def stop_process(process: subprocess.Popen[bytes] | None, name: str) -> None:
    if process is None or process.poll() is not None:
        return
    print(f"Stopping {name}...")
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=8)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)


def backend_python_command() -> str:
    virtual_environment_python = REPOSITORY_ROOT / ".venv" / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python"
    )
    return str(virtual_environment_python) if virtual_environment_python.is_file() else sys.executable


def validate_environment() -> tuple[str, str]:
    if not (BACKEND_DIRECTORY / "app" / "main.py").is_file():
        raise RuntimeError("backend/app/main.py is missing.")
    if not (FRONTEND_DIRECTORY / "package.json").is_file():
        raise RuntimeError("frontend/package.json is missing.")
    if not (BACKEND_DIRECTORY / ".env").is_file():
        raise RuntimeError("backend/.env is missing; copy backend/.env.example first.")
    if not (FRONTEND_DIRECTORY / ".env").is_file():
        raise RuntimeError("frontend/.env is missing; copy frontend/.env.example first.")
    npm_command = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if npm_command is None:
        raise RuntimeError("npm is unavailable on PATH.")
    if not (FRONTEND_DIRECTORY / "node_modules").is_dir():
        raise RuntimeError("Frontend dependencies are missing; run npm install in frontend.")

    python_command = backend_python_command()
    readiness = subprocess.run(
        [python_command, "scripts/check_database.py", "--require-head"],
        cwd=BACKEND_DIRECTORY,
        capture_output=True,
        text=True,
        check=False,
    )
    if readiness.returncode != 0:
        safe_output = (readiness.stdout or readiness.stderr).strip()
        raise RuntimeError(safe_output or "Database readiness check failed.")
    return npm_command, python_command


def main() -> int:
    args = parse_args()
    backend_process: subprocess.Popen[bytes] | None = None
    frontend_process: subprocess.Popen[bytes] | None = None
    worker_process: subprocess.Popen[bytes] | None = None
    windows_job = create_windows_job()
    job_closed = False

    def cleanup() -> None:
        nonlocal job_closed
        stop_process(frontend_process, "frontend")
        stop_process(worker_process, "video worker")
        stop_process(backend_process, "backend")
        if not job_closed:
            close_windows_job(windows_job)
            job_closed = True

    atexit.register(cleanup)
    try:
        if args.backend_port == args.frontend_port:
            raise RuntimeError("Backend and frontend ports must be different.")
        require_port_available(args.backend_port)
        require_port_available(args.frontend_port)
        npm_command, python_command = validate_environment()

        backend_url = f"http://{HOST}:{args.backend_port}"
        frontend_url = f"http://{HOST}:{args.frontend_port}"
        backend_command = [
            python_command,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            HOST,
            "--port",
            str(args.backend_port),
        ]
        if not args.no_reload:
            backend_command.append("--reload")

        child_environment = os.environ.copy()
        child_environment.update(
            {
                "PYTHONUNBUFFERED": "1",
                "VITE_API_URL": f"{backend_url}/api/v1",
            }
        )
        if args.with_worker:
            try:
                with socket.create_connection((HOST, 6379), timeout=1):
                    pass
            except OSError as error:
                raise RuntimeError("Redis is unavailable on 127.0.0.1:6379. Run scripts/start-redis.ps1 first.") from error
            child_environment.setdefault("REDIS_URL", "redis://127.0.0.1:6379/0")
            child_environment.setdefault("CELERY_BROKER_URL", child_environment["REDIS_URL"])
            child_environment.setdefault("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/1")
            worker_command = [python_command, "-m", "celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"]
            if os.name == "nt":
                worker_command.append("--pool=solo")
            print("Starting video worker...")
            worker_process = subprocess.Popen(worker_command, cwd=BACKEND_DIRECTORY, env=child_environment, **process_options())
            assign_to_windows_job(windows_job, worker_process)
            time.sleep(2)
            if worker_process.poll() is not None:
                raise RuntimeError(f"Video worker exited during startup with code {worker_process.returncode}.")

        print(f"Starting backend: {backend_url}")
        backend_process = subprocess.Popen(
            backend_command,
            cwd=BACKEND_DIRECTORY,
            env=child_environment,
            **process_options(),
        )
        assign_to_windows_job(windows_job, backend_process)
        health_body = wait_for_url(
            f"{backend_url}/api/v1/health", backend_process, "Backend"
        )
        health = json.loads(health_body)
        if health.get("database") != "ok":
            raise RuntimeError("Backend started, but database health is not ok.")

        print(f"Starting frontend: {frontend_url}")
        frontend_process = subprocess.Popen(
            [
                npm_command,
                "run",
                "dev",
                "--",
                "--host",
                HOST,
                "--port",
                str(args.frontend_port),
                "--strictPort",
            ],
            cwd=FRONTEND_DIRECTORY,
            env=child_environment,
            **process_options(),
        )
        assign_to_windows_job(windows_job, frontend_process)
        wait_for_url(frontend_url, frontend_process, "Frontend")

        print("\nDeepSight development servers are ready.")
        print(f"Web application: {frontend_url}")
        print(f"API documentation: {backend_url}/docs")
        print("Press Ctrl+C to stop both servers.\n")
        if not args.no_browser:
            webbrowser.open(frontend_url)

        while True:
            if backend_process.poll() is not None:
                raise RuntimeError(
                    f"Backend stopped unexpectedly with code {backend_process.returncode}."
                )
            if frontend_process.poll() is not None:
                raise RuntimeError(
                    f"Frontend stopped unexpectedly with code {frontend_process.returncode}."
                )
            if worker_process is not None and worker_process.poll() is not None:
                raise RuntimeError(f"Video worker stopped unexpectedly with code {worker_process.returncode}.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping DeepSight development servers...")
        return 0
    except (RuntimeError, json.JSONDecodeError) as error:
        print(f"Startup failed: {error}", file=sys.stderr)
        return 1
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
