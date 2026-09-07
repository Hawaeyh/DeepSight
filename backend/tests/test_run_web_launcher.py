import importlib.util
import socket
from pathlib import Path

import pytest


RUN_WEB_PATH = Path(__file__).resolve().parents[2] / "run_web.py"


def load_launcher():
    specification = importlib.util.spec_from_file_location("run_web", RUN_WEB_PATH)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_launcher_uses_loopback_addresses() -> None:
    launcher = load_launcher()
    assert launcher.HOST == "127.0.0.1"
    assert launcher.DEFAULT_BACKEND_PORT == 8000
    assert launcher.DEFAULT_FRONTEND_PORT == 5173
    assert Path(launcher.backend_python_command()).is_file()


def test_launcher_rejects_an_occupied_port() -> None:
    launcher = load_launcher()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((launcher.HOST, 0))
        listener.listen()
        with pytest.raises(RuntimeError, match="already in use"):
            launcher.require_port_available(listener.getsockname()[1])
