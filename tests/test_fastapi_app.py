from fastapi.testclient import TestClient

from main import app


def test_ask_endpoint_returns_answer(monkeypatch):
    async def fake_handle_query(agent, question, thread_id):
        assert agent is not None
        assert question == "What is my portfolio?"
        assert thread_id == "test-session"
        return "Portfolio is healthy."

    app.state.agent = object()
    app.state.session_id = "test-session"
    monkeypatch.setattr("main.handle_query", fake_handle_query)

    client = TestClient(app)
    response = client.post("/ask", json={"question": "What is my portfolio?"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Portfolio is healthy.",
        "session_id": "test-session",
    }
