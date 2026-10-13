"""Small local SQLite store. Replace with PostgreSQL before shared deployment."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4
from .config import database_path

PRESETS = [
    ("Architect", "Plans architecture, constraints, and interfaces."),
    ("Coder", "Implements scoped changes and explains them."),
    ("Debugger", "Investigates reproducible failures and tests fixes."),
    ("Designer", "Designs useful, accessible interfaces."),
    ("Reviewer", "Evaluates code quality, risks, and test coverage."),
    ("Researcher", "Investigates documentation and alternatives."),
    ("DevOps", "Plans build and deployment workflows requiring approval."),
    ("Project Manager", "Breaks work into concrete, testable milestones."),
    ("Tester", "Designs tests and checks edge cases."),
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def connect():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=20)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL,
            instructions TEXT NOT NULL, is_preset INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
            agent_id TEXT NOT NULL REFERENCES agents(id),
            status TEXT NOT NULL CHECK(status IN ('queued','running','completed','failed','cancelled')),
            result TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
            kind TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY, scope TEXT NOT NULL CHECK(scope IN ('project','agent')),
            agent_id TEXT REFERENCES agents(id), content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            CHECK ((scope='project' AND agent_id IS NULL) OR (scope='agent' AND agent_id IS NOT NULL))
        );
        """)
        for name, description in PRESETS:
            stable_id = "preset-" + name.lower().replace(" ", "-")
            db.execute("INSERT OR IGNORE INTO agents VALUES (?,?,?,?,?,?)",
                       (stable_id, name, description, f"You are the {name} specialist. {description} Stay within the user's request, do not pretend to have executed tools or changed files. Respond clearly and briefly.", 1, now()))

def fetch_all(sql, args=()):
    with connect() as db:
        return [dict(row) for row in db.execute(sql, args).fetchall()]

def fetch_one(sql, args=()):
    with connect() as db:
        row = db.execute(sql, args).fetchone()
        return dict(row) if row is not None else None

def add_event(task_id: str, kind: str, detail: str):
    with connect() as db:
        db.execute("INSERT INTO events VALUES (?,?,?,?,?)", (str(uuid4()), task_id, kind, detail, now()))
