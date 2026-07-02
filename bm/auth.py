"""Authentication helpers: password hashing, login and credential generation."""
import hashlib
import hmac
import os
import secrets
import string

from bm import db

_PBKDF2_ROUNDS = 200_000


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Return (hex_hash, hex_salt) for a password using PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ROUNDS
    )
    return dk.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    candidate, _ = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)


def authenticate(username: str, password: str) -> dict | None:
    """Return the user row (as a dict) on success, otherwise None."""
    conn = db.get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1",
        (username.strip().lower(),),
    ).fetchone()
    if row is None:
        return None
    if not verify_password(password, row["password_hash"], row["salt"]):
        return None
    return dict(row)


def set_password(user_id: int, new_password: str, clear_must_change: bool = True) -> None:
    pw_hash, salt = hash_password(new_password)
    conn = db.get_conn()
    conn.execute(
        "UPDATE users SET password_hash = ?, salt = ?, must_change_password = ? WHERE id = ?",
        (pw_hash, salt, 0 if clear_must_change else 1, user_id),
    )
    conn.commit()


def generate_password(length: int = 10) -> str:
    """Generate a readable one-time password (letters + digits)."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_username(prefix: str) -> str:
    """Generate a unique username with the given prefix, e.g. patient-3f9a2b."""
    conn = db.get_conn()
    while True:
        candidate = f"{prefix}-{secrets.token_hex(3)}"
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (candidate,)
        ).fetchone()
        if exists is None:
            return candidate
