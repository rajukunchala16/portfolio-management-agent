"""Run the FastAPI API and Streamlit UI in the same container."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = int(os.getenv("PORT", "8000"))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))


def start_process(command: list[str]) -> subprocess.Popen[str]:
    """Start a child process and return the handle."""
    return subprocess.Popen(
        command,
        cwd=str(ROOT),
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )


api_process = start_process(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(PORT),
    ]
)

streamlit_process = start_process(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.address",
        "0.0.0.0",
        "--server.port",
        str(STREAMLIT_PORT),
    ]
)

try:
    api_process.wait()
finally:
    streamlit_process.terminate()
    api_process.terminate()
