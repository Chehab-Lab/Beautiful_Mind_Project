"""SQLite persistence layer for the BeautifulMind Streamlit app.

A single self-contained database replaces the previous Postgres + Django stack.
The schema mirrors the domain of the original service: users with roles,
doctors, patients, anonymized notes, and per-request usage events, plus a
key/value table for application secrets managed by the admin.
"""
import os
import sqlite3
import threading

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "beautifulmind.db")

_local = threading.local()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    username             TEXT UNIQUE NOT NULL,
    password_hash        TEXT NOT NULL,
    salt                 TEXT NOT NULL,
    role                 TEXT NOT NULL CHECK (role IN ('DOCTOR', 'PATIENT', 'ADMIN')),
    must_change_password INTEGER NOT NULL DEFAULT 0,
    is_active            INTEGER NOT NULL DEFAULT 1,
    created_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS doctors (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    phone_number TEXT
);

CREATE TABLE IF NOT EXISTS patients (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                   INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    doctor_id                 INTEGER REFERENCES doctors(id) ON DELETE SET NULL,
    alias                     TEXT NOT NULL DEFAULT '',
    gender                    TEXT NOT NULL DEFAULT 'O' CHECK (gender IN ('M', 'F', 'O')),
    age                       INTEGER,
    married                   INTEGER NOT NULL DEFAULT 0,
    mental_illness_diagnostic TEXT NOT NULL DEFAULT '',
    medications               TEXT NOT NULL DEFAULT '',
    smoke                     INTEGER NOT NULL DEFAULT 0,
    weekly_sport_activity     TEXT NOT NULL DEFAULT '',
    occupation                TEXT NOT NULL DEFAULT '',
    created_at                TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    anonymized_text  TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usage_events (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id         INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    note_id            INTEGER REFERENCES notes(id) ON DELETE SET NULL,
    duration_seconds   REAL NOT NULL DEFAULT 0,
    transcribed_tokens INTEGER NOT NULL DEFAULT 0,
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS secrets (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_conn() -> sqlite3.Connection:
    """Return a thread-local SQLite connection.

    Streamlit reruns scripts on multiple threads, so a connection per thread
    keeps sqlite3 happy while still being cheap.
    """
    conn = getattr(_local, "conn", None)
    if conn is None:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        _local.conn = conn
    return conn


def init_db() -> None:
    """Create tables (idempotent) and seed the default admin account."""
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    _seed_default_admin()


def _seed_default_admin() -> None:
    """Seed a bootstrap admin (admin/admin) that must be changed on first login.

    The default credentials only exist to bootstrap a fresh deployment. The
    ``must_change_password`` flag forces a new password before the admin can do
    anything, so the well-known default is never a standing way in.
    """
    from bm import auth  # local import to avoid a cycle

    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM users WHERE role = 'ADMIN' LIMIT 1"
    ).fetchone()
    if row is None:
        pw_hash, salt = auth.hash_password("admin")
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, role, must_change_password) "
            "VALUES (?, ?, ?, 'ADMIN', 1)",
            ("admin", pw_hash, salt),
        )
        conn.commit()
