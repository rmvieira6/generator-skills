from __future__ import annotations

import atexit
import hashlib
import json
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


def _api_fingerprint() -> str:
    digest = hashlib.sha256()
    watched_paths = [
        ROOT / "laucher.py",
        ROOT / "apps" / "api" / "pyproject.toml",
    ]
    watched_paths.extend(sorted((ROOT / "apps" / "api" / "src").rglob("*.py")))

    for path in watched_paths:
        stat = path.stat()
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(str(stat.st_mtime_ns).encode("utf-8"))
        digest.update(str(stat.st_size).encode("utf-8"))

    return digest.hexdigest()


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


def _wait_for_route(base_url: str, route_path: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    openapi_url = f"{base_url}/openapi.json"

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(openapi_url, timeout=2) as response:
                if response.status != 200:
                    time.sleep(0.5)
                    continue
                payload = json.loads(response.read().decode("utf-8"))
                paths = payload.get("paths", {})
                if route_path in paths:
                    return
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            time.sleep(0.5)
            continue

        time.sleep(0.5)

    raise RuntimeError(
        f"API subiu sem expor a rota obrigatoria {route_path} em {openapi_url}"
    )


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
def _start_api(api_fingerprint: str) -> tuple[subprocess.Popen[str], str]:
    del api_fingerprint
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
    _wait_for_route(base_url, "/api/generation/optimize-skill")
    return process, base_url


def main() -> None:
    _, base_url = _start_api(_api_fingerprint())
    os.environ["SKILL_FORGE_API_URL"] = base_url

    web_src = str(WEB_SRC_DIR)
    if web_src not in sys.path:
        sys.path.insert(0, web_src)

    runpy.run_path(str(WEB_APP_FILE), run_name="__main__")


main()