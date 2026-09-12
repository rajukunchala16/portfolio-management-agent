from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

logger = logging.getLogger(
    "mcp-client"
)


def get_mcp_client() -> MultiServerMCPClient:
    """
    Create the MCP client used by the AI agent.

    The CoinDCX MCP server is intentionally kept
    as a separate process.
    """

    project_root = Path(__file__).resolve().parents[1]
    server_module = os.getenv(
        "COINDCX_MCP_SERVER_MODULE",
        "mcp_intigration.coindcx.server",
    )
    python_executable = sys.executable

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(project_root) if not existing_pythonpath else (
        f"{project_root}{os.pathsep}{existing_pythonpath}"
    )

    logger.info(
        "Creating CoinDCX MCP client"
    )

    client = MultiServerMCPClient(
        {
            "coindcx": {
                "transport": "stdio",
                "command": python_executable,
                "args": [
                    "-m",
                    server_module,
                ],
                "cwd": str(project_root),
                "env": env,
            }
        }
    )

    logger.info(
        "CoinDCX MCP client created"
    )

    return client