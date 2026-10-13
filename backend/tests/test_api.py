"""Contract checks for the real local API, with a clearly mocked model adapter."""
import pytest
from fastapi.testclient import TestClient
from agentos.main import app, get_completion

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_DB_PATH", str(tmp_path / "agentos.sqlite3"))
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_health_and_presets(client):
    assert client.get("/healthz").json()["status"] == "ok"
    agents = client.get("/api/v1/agents").json()
    assert len(agents) == 9
    assert {a["name"] for a in agents} >= {"Coder", "Designer", "Reviewer"}

def test_create_custom_agent(client):
    result = client.post("/api/v1/agents", json={"name": "Docs Helper", "description": "Writes docs", "instructions": "Explain Python code precisely and safely."})
    assert result.status_code == 201
    agent = result.json()
    assert agent["is_preset"] == 0
    assert any(a["id"] == agent["id"] for a in client.get("/api/v1/agents").json())

def test_task_requires_real_agent(client):
    response = client.post("/api/v1/tasks", json={"title": "Write tests", "description": "Write focused unit tests", "agent_id": "nonexistent"})
    assert response.status_code == 404

def make_task(client):
    agent = next(a for a in client.get("/api/v1/agents").json() if a["name"] == "Coder")
    result = client.post("/api/v1/tasks", json={"title": "Explain loops", "description": "Explain for loops with an example", "agent_id": agent["id"]})
    assert result.status_code == 201
    return result.json()

def test_task_lifecycle_and_events(client):
    task = make_task(client)
    assert task["status"] == "queued"
    events = client.get(f'/api/v1/tasks/{task["id"]}/events').json()
    assert [e["kind"] for e in events] == ["created"]
    cancelled = client.post(f'/api/v1/tasks/{task["id"]}/cancel')
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert client.post(f'/api/v1/tasks/{task["id"]}/cancel').status_code == 409

def test_no_key_refuses_to_fake_execution(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AGENTOS_MODEL", raising=False)
    task = make_task(client)
    response = client.post(f'/api/v1/tasks/{task["id"]}/run')
    assert response.status_code == 409
    assert client.get(f'/api/v1/tasks/{task["id"]}').json()["status"] == "queued"

def test_run_uses_explicit_mock_provider_in_tests_only(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    monkeypatch.setenv("AGENTOS_MODEL", "test-model")
    saved = client.post("/api/v1/memories", json={"scope": "project", "content": "Always explain changes before editing files."})
    assert saved.status_code == 201
    recorded = {}
    async def fake_completion(instructions, prompt, memories):
        recorded.update({"instructions": instructions, "prompt": prompt, "memories": memories})
        return "A loop repeats a sequence of statements."
    app.dependency_overrides[get_completion] = lambda: fake_completion
    task = make_task(client)
    response = client.post(f'/api/v1/tasks/{task["id"]}/run')
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert "loop" in response.json()["result"]
    assert recorded["memories"] == [saved.json()["content"]]
    assert [e["kind"] for e in client.get(f'/api/v1/tasks/{task["id"]}/events').json()] == ["created", "running", "completed"]
    assert client.post(f'/api/v1/tasks/{task["id"]}/run').status_code == 409

def test_memory_create_and_delete(client):
    created = client.post("/api/v1/memories", json={"scope": "project", "content": "Keep user secrets off GitHub."})
    assert created.status_code == 201
    identifier = created.json()["id"]
    assert len(client.get("/api/v1/memories").json()) == 1
    assert client.delete(f"/api/v1/memories/{identifier}").status_code == 204
    assert client.get("/api/v1/memories").json() == []

def test_scope_validation(client):
    assert client.post("/api/v1/memories", json={"scope": "agent", "content": "Agent note without agent"}).status_code == 422
    assert client.post("/api/v1/memories", json={"scope": "project", "agent_id": "arbitrary", "content": "Invalid project note"}).status_code == 422
