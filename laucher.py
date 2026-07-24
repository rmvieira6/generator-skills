from __future__ import annotations

import atexit
import os
import runpy
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
API_APP_DIR = ROOT / "apps" / "api"
WEB_APP_FILE = ROOT / "apps" / "web" / "src" / "app.py"
WEB_SRC_DIR = ROOT / "apps" / "web" / "src"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(base_url: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    health_url = f"{base_url}/health"

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.5)

    raise RuntimeError(f"API nao respondeu em {health_url} dentro de {timeout_seconds:.0f}s")


def _stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


@st.cache_resource(show_spinner=False)
def _start_api() -> tuple[subprocess.Popen[str], str]:
    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["SKILL_FORGE_API_URL"] = base_url

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.main:app",
        "--port",
        str(port),
        "--app-dir",
        str(API_APP_DIR),
        "--loop",
        "asyncio",
    ]

    process = subprocess.Popen(
        command,
        cwd=str(ROOT),
        env=env,
        text=True,
    )
    atexit.register(_stop_process, process)
    _wait_for_health(base_url)
    return process, base_url


def main() -> None:
    _, base_url = _start_api()
    os.environ["SKILL_FORGE_API_URL"] = base_url

    web_src = str(WEB_SRC_DIR)
    if web_src not in sys.path:
        sys.path.insert(0, web_src)

    runpy.run_path(str(WEB_APP_FILE), run_name="__main__")


main()