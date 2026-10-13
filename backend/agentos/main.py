"""AgentOS prototype: a local-only API. Do not expose to the public internet."""
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from . import db
from .config import model_settings
from .providers import request_completion

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield

app = FastAPI(title="AgentOS Starter API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type"])

class NewAgent(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=1, max_length=400)
    instructions: str = Field(min_length=10, max_length=8000)

class NewTask(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=3, max_length=5000)
    agent_id: str

class NewMemory(BaseModel):
    scope: str = Field(pattern="^(project|agent)$")
    agent_id: str | None = None
    content: str = Field(min_length=3, max_length=4000)

async def get_completion():
    return request_completion

@app.get("/healthz")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/api/v1/system")
def system_status():
    return {"runtime": "local-only", "model_configured": model_settings() is not None,
            "capabilities": ["agents", "tasks", "events", "project-memory", "openai-compatible-chat"]}

@app.get("/api/v1/agents")
def agents():
    return db.fetch_all("SELECT * FROM agents ORDER BY is_preset DESC, name")

@app.post("/api/v1/agents", status_code=201)
def create_agent(agent: NewAgent):
    identifier = str(uuid4())
    with db.connect() as connection:
        connection.execute("INSERT INTO agents VALUES (?,?,?,?,?,?)", (identifier, agent.name, agent.description, agent.instructions, 0, db.now()))
    return db.fetch_one("SELECT * FROM agents WHERE id=?", (identifier,))

@app.get("/api/v1/tasks")
def tasks():
    return db.fetch_all("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 100")

@app.post("/api/v1/tasks", status_code=201)
def create_task(task: NewTask):
    if not db.fetch_one("SELECT id FROM agents WHERE id=?", (task.agent_id,)):
        raise HTTPException(status_code=404, detail="Agent does not exist")
    identifier = str(uuid4())
    moment = db.now()
    with db.connect() as connection:
        connection.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?)", (identifier, task.title, task.description, task.agent_id, "queued", None, moment, moment))
    db.add_event(identifier, "created", "Task queued")
    return db.fetch_one("SELECT * FROM tasks WHERE id=?", (identifier,))

@app.get("/api/v1/tasks/{task_id}")
def task_detail(task_id: str):
    task = db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))
    if task is None:
        raise HTTPException(status_code=404, detail="Task does not exist")
    return task

@app.get("/api/v1/tasks/{task_id}/events")
def task_events(task_id: str):
    if not db.fetch_one("SELECT id FROM tasks WHERE id=?", (task_id,)):
        raise HTTPException(status_code=404, detail="Task does not exist")
    return db.fetch_all("SELECT * FROM events WHERE task_id=? ORDER BY created_at, rowid", (task_id,))

@app.post("/api/v1/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    # Only queued tasks can be safely cancelled in this synchronous prototype.
    with db.connect() as connection:
        cursor = connection.execute("UPDATE tasks SET status='cancelled',updated_at=? WHERE id=? AND status='queued'", (db.now(), task_id))
        if not cursor.rowcount:
            raise HTTPException(status_code=409, detail="Only queued tasks can be cancelled in this prototype")
    db.add_event(task_id, "cancelled", "Task cancelled before execution")
    return db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))

@app.post("/api/v1/tasks/{task_id}/run")
async def run_task(task_id: str, completion=Depends(get_completion)):
    task = db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))
    if task is None:
        raise HTTPException(status_code=404, detail="Task does not exist")
    if model_settings() is None:
        raise HTTPException(status_code=409, detail="Model not configured. Set OPENAI_API_KEY and AGENTOS_MODEL.")
    with db.connect() as connection:
        updated = connection.execute("UPDATE tasks SET status='running',updated_at=? WHERE id=? AND status='queued'", (db.now(), task_id))
        if updated.rowcount != 1:
            raise HTTPException(status_code=409, detail="Task is not queued")
    db.add_event(task_id, "running", "Model request started")
    agent = db.fetch_one("SELECT * FROM agents WHERE id=?", (task["agent_id"],))
    notes = [m["content"] for m in db.fetch_all("SELECT content FROM memories WHERE scope='project' OR (scope='agent' AND agent_id=?) ORDER BY created_at DESC LIMIT 8", (task["agent_id"],))]
    try:
        result = await completion(agent["instructions"], task["description"], notes)
        with db.connect() as connection:
            connection.execute("UPDATE tasks SET status='completed', result=?,updated_at=? WHERE id=?", (result, db.now(), task_id))
        db.add_event(task_id, "completed", "Model returned a response")
    except Exception as exc:
        # Keep API error content safe; details of provider exceptions can expose request data.
        with db.connect() as connection:
            connection.execute("UPDATE tasks SET status='failed',updated_at=? WHERE id=?", (db.now(), task_id))
        db.add_event(task_id, "failed", "Agent model request did not complete")
        raise HTTPException(status_code=502, detail="Agent request failed") from exc
    return db.fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))

@app.get("/api/v1/memories")
def memories():
    return db.fetch_all("SELECT * FROM memories ORDER BY created_at DESC LIMIT 100")

@app.post("/api/v1/memories", status_code=201)
def create_memory(memory: NewMemory):
    if (memory.scope == "project" and memory.agent_id is not None) or (memory.scope == "agent" and not memory.agent_id):
        raise HTTPException(status_code=422, detail="Agent memory requires agent_id; project memory must omit it")
    if memory.agent_id and not db.fetch_one("SELECT id FROM agents WHERE id=?", (memory.agent_id,)):
        raise HTTPException(status_code=404, detail="Agent does not exist")
    identifier = str(uuid4())
    with db.connect() as connection:
        connection.execute("INSERT INTO memories VALUES (?,?,?,?,?)", (identifier, memory.scope, memory.agent_id, memory.content, db.now()))
    return db.fetch_one("SELECT * FROM memories WHERE id=?", (identifier,))

@app.delete("/api/v1/memories/{memory_id}", status_code=204)
def delete_memory(memory_id: str):
    with db.connect() as connection:
        row = connection.execute("DELETE FROM memories WHERE id=?", (memory_id,))
        if not row.rowcount:
            raise HTTPException(status_code=404, detail="Memory does not exist")
