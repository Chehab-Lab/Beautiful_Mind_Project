"""Data-access functions for users, doctors, patients, notes and usage."""
from bm import auth, db


# ---------------------------------------------------------------------------
# Doctors
# ---------------------------------------------------------------------------
def create_doctor(username, password, first_name, last_name, phone_number,
                  must_change_password=False):
    pw_hash, salt = auth.hash_password(password)
    row = db.query(
        "INSERT INTO users (username, password_hash, salt, role, must_change_password) "
        "VALUES (%s, %s, %s, 'DOCTOR', %s) RETURNING id",
        (username.strip().lower(), pw_hash, salt, bool(must_change_password)),
        fetch="one",
    )
    user_id = row["id"]
    db.query(
        "INSERT INTO doctors (user_id, first_name, last_name, phone_number) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, first_name, last_name, phone_number),
        commit=True,
    )
    return get_doctor_by_user(user_id)


def get_doctor_by_user(user_id):
    row = db.query("SELECT * FROM doctors WHERE user_id = %s", (user_id,), fetch="one")
    return dict(row) if row else None


def list_doctors():
    rows = db.query(
        "SELECT d.*, u.username, u.is_active FROM doctors d "
        "JOIN users u ON u.id = d.user_id ORDER BY d.last_name, d.first_name",
        fetch="all",
    )
    return [dict(r) for r in rows]


def update_doctor(doctor_id, first_name, last_name, phone_number):
    db.query(
        "UPDATE doctors SET first_name = %s, last_name = %s, phone_number = %s WHERE id = %s",
        (first_name, last_name, phone_number, doctor_id),
        commit=True,
    )


def delete_user_cascade(user_id):
    """Delete a user; ON DELETE CASCADE removes the doctor/patient profile,
    notes and usage events."""
    db.query("DELETE FROM users WHERE id = %s", (user_id,), commit=True)


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------
def create_patient(doctor_id=None, **fields):
    """Create a patient plus its login user. Returns (patient, username, one_time_password)."""
    username = auth.generate_username("patient")
    one_time_password = auth.generate_password()
    pw_hash, salt = auth.hash_password(one_time_password)
    row = db.query(
        "INSERT INTO users (username, password_hash, salt, role, must_change_password) "
        "VALUES (%s, %s, %s, 'PATIENT', TRUE) RETURNING id",
        (username, pw_hash, salt),
        fetch="one",
    )
    user_id = row["id"]
    db.query(
        """INSERT INTO patients
           (user_id, doctor_id, alias, gender, age, married,
            mental_illness_diagnostic, medications, smoke,
            weekly_sport_activity, occupation)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            user_id,
            doctor_id,
            fields.get("alias", ""),
            fields.get("gender", "O"),
            fields.get("age"),
            bool(fields.get("married")),
            fields.get("mental_illness_diagnostic", ""),
            fields.get("medications", ""),
            bool(fields.get("smoke")),
            fields.get("weekly_sport_activity", ""),
            fields.get("occupation", ""),
        ),
        commit=True,
    )
    patient = get_patient_by_user(user_id)
    return patient, username, one_time_password


def get_patient_by_user(user_id):
    row = db.query("SELECT * FROM patients WHERE user_id = %s", (user_id,), fetch="one")
    return dict(row) if row else None


def get_patient(patient_id):
    row = db.query("SELECT * FROM patients WHERE id = %s", (patient_id,), fetch="one")
    return dict(row) if row else None


def list_patients(doctor_id=None):
    sql = (
        "SELECT p.*, u.username, u.is_active FROM patients p "
        "JOIN users u ON u.id = p.user_id"
    )
    params = ()
    if doctor_id is not None:
        sql += " WHERE p.doctor_id = %s"
        params = (doctor_id,)
    sql += " ORDER BY p.created_at DESC"
    rows = db.query(sql, params, fetch="all")
    return [dict(r) for r in rows]


def update_patient(patient_id, **fields):
    columns = [
        "alias", "gender", "age", "married", "mental_illness_diagnostic",
        "medications", "smoke", "weekly_sport_activity", "occupation", "doctor_id",
    ]
    sets, params = [], []
    for col in columns:
        if col in fields:
            value = fields[col]
            if col in ("married", "smoke"):
                value = bool(value)
            sets.append(f"{col} = %s")
            params.append(value)
    if not sets:
        return
    params.append(patient_id)
    db.query(f"UPDATE patients SET {', '.join(sets)} WHERE id = %s", tuple(params), commit=True)


def reset_patient_password(user_id):
    """Issue a fresh one-time password for a patient. Returns the plain password."""
    one_time_password = auth.generate_password()
    auth.set_password(user_id, one_time_password, clear_must_change=False)
    db.query(
        "UPDATE users SET must_change_password = TRUE WHERE id = %s", (user_id,), commit=True
    )
    return one_time_password


# ---------------------------------------------------------------------------
# Notes & usage
# ---------------------------------------------------------------------------
def add_note_with_usage(patient_id, anonymized_text, duration_seconds, transcribed_tokens):
    row = db.query(
        "INSERT INTO notes (patient_id, anonymized_text) VALUES (%s, %s) RETURNING id",
        (patient_id, anonymized_text),
        fetch="one",
    )
    note_id = row["id"]
    db.query(
        "INSERT INTO usage_events (patient_id, note_id, duration_seconds, transcribed_tokens) "
        "VALUES (%s, %s, %s, %s)",
        (patient_id, note_id, duration_seconds, transcribed_tokens),
        commit=True,
    )
    return note_id


def list_notes(patient_id):
    rows = db.query(
        "SELECT * FROM notes WHERE patient_id = %s ORDER BY created_at DESC",
        (patient_id,),
        fetch="all",
    )
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Usage statistics
# ---------------------------------------------------------------------------
def usage_totals():
    """Aggregated usage across all patients."""
    row = db.query(
        "SELECT COUNT(*) AS voice_requests, "
        "COALESCE(SUM(duration_seconds), 0) AS total_duration, "
        "COALESCE(SUM(transcribed_tokens), 0) AS total_tokens FROM usage_events",
        fetch="one",
    )
    return dict(row)


def usage_per_patient():
    """Per-patient usage rows, including patients with no activity yet."""
    rows = db.query(
        """SELECT p.id AS patient_id, p.alias, u.username,
                  COUNT(e.id) AS voice_requests,
                  COALESCE(SUM(e.duration_seconds), 0) AS total_duration,
                  COALESCE(SUM(e.transcribed_tokens), 0) AS total_tokens
           FROM patients p
           JOIN users u ON u.id = p.user_id
           LEFT JOIN usage_events e ON e.patient_id = p.id
           GROUP BY p.id, u.username
           ORDER BY voice_requests DESC, p.alias""",
        fetch="all",
    )
    return [dict(r) for r in rows]
