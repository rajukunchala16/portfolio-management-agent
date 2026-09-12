from pathlib import Path

from mcp_intigration.mcp_client import get_mcp_client


def test_mcp_client_uses_project_root_and_module_entrypoint():
    client = get_mcp_client()
    connection = client.connections["coindcx"]

    assert connection["command"].endswith("python.exe") or connection["command"].endswith("python")
    assert connection["cwd"] == str(Path(__file__).resolve().parents[1])
    assert "-m" in connection["args"]
    assert "mcp_intigration.coindcx.server" in connection["args"]
