import sqlite3
from datetime import datetime, timezone

from flask import current_app, g

MIGRATIONS = [
    # 1: users + audit log
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        name TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin','student')),
        password_hash TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        failed_logins INTEGER NOT NULL DEFAULT 0,
        locked_until TEXT,
        created_at TEXT NOT NULL,
        last_login_at TEXT
    );
    CREATE TABLE audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        actor_id INTEGER,
        action TEXT NOT NULL,
        target TEXT,
        ip TEXT,
        detail TEXT
    );
    CREATE INDEX idx_audit_ts ON audit_log(ts);
    """,
]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def migrate(path: str) -> int:
    """Apply pending migrations. Returns the resulting schema version."""
    conn = connect(path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
        row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
        current = row["v"] or 0
        for number, script in enumerate(MIGRATIONS, start=1):
            if number > current:
                conn.executescript(script)
                conn.execute("INSERT INTO schema_version (version) VALUES (?)", (number,))
                conn.commit()
        return len(MIGRATIONS)
    finally:
        conn.close()


def audit(action: str, actor_id=None, target=None, ip=None, detail=None):
    db = get_db()
    db.execute(
        "INSERT INTO audit_log (ts, actor_id, action, target, ip, detail) VALUES (?,?,?,?,?,?)",
        (utcnow(), actor_id, action, target, ip, detail),
    )
    db.commit()
