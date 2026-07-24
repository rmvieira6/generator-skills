from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _start_process(name: str, command: list[str]) -> subprocess.Popen[str]:
    print(f"[START] {name}: {' '.join(command)}")
    return subprocess.Popen(
        command,
        cwd=str(ROOT),
        env=os.environ.copy(),
        text=True,
    )


def _stop_process(name: str, process: subprocess.Popen[str], timeout: float = 8.0) -> None:
    if process.poll() is not None:
        return

    print(f"[STOP] Finalizando {name}...")
    process.terminate()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[STOP] {name} nao encerrou no tempo esperado; forçando kill.")
        process.kill()
        process.wait(timeout=3.0)


def main() -> int:
    python_executable = sys.executable

    api_command = [
        python_executable,
        "-m",
        "uvicorn",
        "src.main:app",
        "--reload",
        "--port",
        "8000",
        "--app-dir",
        "apps/api",
        "--loop",
        "asyncio",
    ]

    web_command = [
        python_executable,
        "-m",
        "streamlit",
        "run",
        "apps/web/src/app.py",
    ]

    print("Iniciando Skill Forge (API + Web)...")
    print("API: http://localhost:8000")
    print("Web: http://localhost:8501")
    print("Pressione Ctrl+C nesta janela para encerrar ambos.")

    api_process = _start_process("API", api_command)
    time.sleep(1.0)
    web_process = _start_process("Web", web_command)

    processes = [("API", api_process), ("Web", web_process)]
    exit_code = 0

    try:
        while True:
            for name, process in processes:
                code = process.poll()
                if code is not None:
                    print(f"[EXIT] {name} finalizou com codigo {code}.")
                    exit_code = code or 0
                    raise KeyboardInterrupt
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        for name, process in reversed(processes):
            _stop_process(name, process)

    print("Skill Forge finalizado.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
