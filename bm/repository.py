"""Data-access functions for users, doctors, patients, notes and usage."""
from bm import auth, db


# ---------------------------------------------------------------------------
# Doctors
# ---------------------------------------------------------------------------
def create_doctor(username, password, first_name, last_name, phone_number,
                  must_change_password=False):
    conn = db.get_conn()
    pw_hash, salt = auth.hash_password(password)
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, salt, role, must_change_password) "
        "VALUES (?, ?, ?, 'DOCTOR', ?)",
        (username.strip().lower(), pw_hash, salt, 1 if must_change_password else 0),
    )
    user_id = cur.lastrowid
    conn.execute(
        "INSERT INTO doctors (user_id, first_name, last_name, phone_number) "
        "VALUES (?, ?, ?, ?)",
        (user_id, first_name, last_name, phone_number),
    )
    conn.commit()
    return get_doctor_by_user(user_id)


def get_doctor_by_user(user_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM doctors WHERE user_id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def list_doctors():
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT d.*, u.username, u.is_active FROM doctors d "
        "JOIN users u ON u.id = d.user_id ORDER BY d.last_name, d.first_name"
    ).fetchall()
    return [dict(r) for r in rows]


def update_doctor(doctor_id, first_name, last_name, phone_number):
    conn = db.get_conn()
    conn.execute(
        "UPDATE doctors SET first_name = ?, last_name = ?, phone_number = ? WHERE id = ?",
        (first_name, last_name, phone_number, doctor_id),
    )
    conn.commit()


def delete_user_cascade(user_id):
    """Delete a user; ON DELETE CASCADE removes the doctor/patient profile,
    notes and usage events."""
    conn = db.get_conn()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------
def create_patient(doctor_id=None, **fields):
    """Create a patient plus its login user. Returns (patient, username, one_time_password)."""
    conn = db.get_conn()
    username = auth.generate_username("patient")
    one_time_password = auth.generate_password()
    pw_hash, salt = auth.hash_password(one_time_password)
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, salt, role, must_change_password) "
        "VALUES (?, ?, ?, 'PATIENT', 1)",
        (username, pw_hash, salt),
    )
    user_id = cur.lastrowid
    conn.execute(
        """INSERT INTO patients
           (user_id, doctor_id, alias, gender, age, married,
            mental_illness_diagnostic, medications, smoke,
            weekly_sport_activity, occupation)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            doctor_id,
            fields.get("alias", ""),
            fields.get("gender", "O"),
            fields.get("age"),
            1 if fields.get("married") else 0,
            fields.get("mental_illness_diagnostic", ""),
            fields.get("medications", ""),
            1 if fields.get("smoke") else 0,
            fields.get("weekly_sport_activity", ""),
            fields.get("occupation", ""),
        ),
    )
    conn.commit()
    patient = get_patient_by_user(user_id)
    return patient, username, one_time_password


def get_patient_by_user(user_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def get_patient(patient_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    return dict(row) if row else None


def list_patients(doctor_id=None):
    conn = db.get_conn()
    sql = (
        "SELECT p.*, u.username, u.is_active FROM patients p "
        "JOIN users u ON u.id = p.user_id"
    )
    params = ()
    if doctor_id is not None:
        sql += " WHERE p.doctor_id = ?"
        params = (doctor_id,)
    sql += " ORDER BY p.created_at DESC"
    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def update_patient(patient_id, **fields):
    conn = db.get_conn()
    columns = [
        "alias", "gender", "age", "married", "mental_illness_diagnostic",
        "medications", "smoke", "weekly_sport_activity", "occupation", "doctor_id",
    ]
    sets, params = [], []
    for col in columns:
        if col in fields:
            value = fields[col]
            if col in ("married", "smoke"):
                value = 1 if value else 0
            sets.append(f"{col} = ?")
            params.append(value)
    if not sets:
        return
    params.append(patient_id)
    conn.execute(f"UPDATE patients SET {', '.join(sets)} WHERE id = ?", params)
    conn.commit()


def reset_patient_password(user_id):
    """Issue a fresh one-time password for a patient. Returns the plain password."""
    one_time_password = auth.generate_password()
    auth.set_password(user_id, one_time_password, clear_must_change=False)
    conn = db.get_conn()
    conn.execute("UPDATE users SET must_change_password = 1 WHERE id = ?", (user_id,))
    conn.commit()
    return one_time_password


# ---------------------------------------------------------------------------
# Notes & usage
# ---------------------------------------------------------------------------
def add_note_with_usage(patient_id, anonymized_text, duration_seconds, transcribed_tokens):
    conn = db.get_conn()
    cur = conn.execute(
        "INSERT INTO notes (patient_id, anonymized_text) VALUES (?, ?)",
        (patient_id, anonymized_text),
    )
    note_id = cur.lastrowid
    conn.execute(
        "INSERT INTO usage_events (patient_id, note_id, duration_seconds, transcribed_tokens) "
        "VALUES (?, ?, ?, ?)",
        (patient_id, note_id, duration_seconds, transcribed_tokens),
    )
    conn.commit()
    return note_id


def list_notes(patient_id):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT * FROM notes WHERE patient_id = ? ORDER BY created_at DESC",
        (patient_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Usage statistics
# ---------------------------------------------------------------------------
def usage_totals():
    """Aggregated usage across all patients."""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS voice_requests, "
        "COALESCE(SUM(duration_seconds), 0) AS total_duration, "
        "COALESCE(SUM(transcribed_tokens), 0) AS total_tokens FROM usage_events"
    ).fetchone()
    return dict(row)


def usage_per_patient():
    """Per-patient usage rows, including patients with no activity yet."""
    conn = db.get_conn()
    rows = conn.execute(
        """SELECT p.id AS patient_id, p.alias, u.username,
                  COUNT(e.id) AS voice_requests,
                  COALESCE(SUM(e.duration_seconds), 0) AS total_duration,
                  COALESCE(SUM(e.transcribed_tokens), 0) AS total_tokens
           FROM patients p
           JOIN users u ON u.id = p.user_id
           LEFT JOIN usage_events e ON e.patient_id = p.id
           GROUP BY p.id
           ORDER BY voice_requests DESC, p.alias"""
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------
def set_secret(key, value):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO secrets (key, value, updated_at) VALUES (?, ?, datetime('now')) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = datetime('now')",
        (key.strip(), value),
    )
    conn.commit()


def get_secret(key, default=None):
    conn = db.get_conn()
    row = conn.execute("SELECT value FROM secrets WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def list_secrets():
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT key, value, updated_at FROM secrets ORDER BY key"
    ).fetchall()
    return [dict(r) for r in rows]


def delete_secret(key):
    conn = db.get_conn()
    conn.execute("DELETE FROM secrets WHERE key = ?", (key,))
    conn.commit()
