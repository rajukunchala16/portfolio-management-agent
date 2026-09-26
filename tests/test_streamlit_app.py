import streamlit_app


def test_get_backend_url_defaults_to_localhost(monkeypatch):
    monkeypatch.delenv("PORTFOLIO_AGENT_API_URL", raising=False)
    assert streamlit_app.get_backend_url() == "http://127.0.0.1:8000"


def test_get_backend_url_uses_env_value(monkeypatch):
    monkeypatch.setenv("PORTFOLIO_AGENT_API_URL", "https://example.com")
    assert streamlit_app.get_backend_url() == "https://example.com"
