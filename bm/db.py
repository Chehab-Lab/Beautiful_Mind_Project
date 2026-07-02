"""PostgreSQL persistence layer (Supabase) for the BeautifulMind app.

The connection string is read from ``st.secrets["DATABASE_URL"]`` (Streamlit
Cloud) or the ``DATABASE_URL`` environment variable. The schema mirrors the
original domain: users with roles, doctors, patients, anonymized notes,
per-request usage events, and a key/value table for application secrets.
"""
import os
import threading

import psycopg2
import psycopg2.extras

_local = threading.local()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                   BIGSERIAL PRIMARY KEY,
    username             TEXT UNIQUE NOT NULL,
    password_hash        TEXT NOT NULL,
    salt                 TEXT NOT NULL,
    role                 TEXT NOT NULL CHECK (role IN ('DOCTOR', 'PATIENT', 'ADMIN')),
    must_change_password BOOLEAN NOT NULL DEFAULT FALSE,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS doctors (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    phone_number TEXT
);

CREATE TABLE IF NOT EXISTS patients (
    id                        BIGSERIAL PRIMARY KEY,
    user_id                   BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    doctor_id                 BIGINT REFERENCES doctors(id) ON DELETE SET NULL,
    alias                     TEXT NOT NULL DEFAULT '',
    gender                    TEXT NOT NULL DEFAULT 'O' CHECK (gender IN ('M', 'F', 'O')),
    age                       INTEGER,
    married                   BOOLEAN NOT NULL DEFAULT FALSE,
    mental_illness_diagnostic TEXT NOT NULL DEFAULT '',
    medications               TEXT NOT NULL DEFAULT '',
    smoke                     BOOLEAN NOT NULL DEFAULT FALSE,
    weekly_sport_activity     TEXT NOT NULL DEFAULT '',
    occupation                TEXT NOT NULL DEFAULT '',
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notes (
    id              BIGSERIAL PRIMARY KEY,
    patient_id      BIGINT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    anonymized_text TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS usage_events (
    id                 BIGSERIAL PRIMARY KEY,
    patient_id         BIGINT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    note_id            BIGINT REFERENCES notes(id) ON DELETE SET NULL,
    duration_seconds   DOUBLE PRECISION NOT NULL DEFAULT 0,
    transcribed_tokens INTEGER NOT NULL DEFAULT 0,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def _dsn() -> str | None:
    dsn = None
    try:
        import streamlit as st

        dsn = st.secrets.get("DATABASE_URL")
    except Exception:  # noqa: BLE001 - no secrets file / not in a Streamlit run
        dsn = None
    return dsn or os.getenv("DATABASE_URL")


def _reset_conn() -> None:
    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass
    _local.conn = None


def get_conn():
    """Return a live thread-local psycopg2 connection."""
    conn = getattr(_local, "conn", None)
    if conn is not None and conn.closed == 0:
        return conn
    dsn = _dsn()
    if not dsn:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in .streamlit/secrets.toml "
            "for local runs, or in the Streamlit Cloud Secrets manager."
        )
    conn = psycopg2.connect(dsn)
    _local.conn = conn
    return conn


def query(sql, params=None, *, fetch=None, commit=False):
    """Run a statement. ``fetch`` is 'one', 'all' or None.

    Retries once on a dropped connection (Supabase pooler can recycle idle
    connections between Streamlit reruns).
    """
    last_exc = None
    for attempt in (1, 2):
        conn = get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params or ())
                if fetch == "one":
                    result = cur.fetchone()
                elif fetch == "all":
                    result = cur.fetchall()
                else:
                    result = None
            if commit:
                conn.commit()
            return result
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
            last_exc = exc
            _reset_conn()  # connection is dead; drop it and retry with a fresh one
        except Exception:
            try:
                conn.rollback()
            except Exception:  # noqa: BLE001
                pass
            raise
    raise last_exc


def init_db() -> None:
    """Create tables (idempotent) and seed the default admin account."""
    query(SCHEMA, commit=True)
    _seed_default_admin()


def _seed_default_admin() -> None:
    """Seed a bootstrap admin (admin/admin) that must be changed on first login.

    The default credentials only exist to bootstrap a fresh deployment. The
    ``must_change_password`` flag forces a new password before the admin can do
    anything, so the well-known default is never a standing way in.
    """
    from bm import auth  # local import to avoid a cycle

    row = query("SELECT id FROM users WHERE role = 'ADMIN' LIMIT 1", fetch="one")
    if row is None:
        pw_hash, salt = auth.hash_password("admin")
        query(
            "INSERT INTO users (username, password_hash, salt, role, must_change_password) "
            "VALUES (%s, %s, %s, 'ADMIN', TRUE)",
            ("admin", pw_hash, salt),
            commit=True,
        )
