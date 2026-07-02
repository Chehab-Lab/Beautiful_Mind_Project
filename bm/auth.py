"""Authentication helpers: password hashing, login and credential generation."""
import hashlib
import hmac
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
    row = db.query(
        "SELECT * FROM users WHERE username = %s AND is_active = TRUE",
        (username.strip().lower(),),
        fetch="one",
    )
    if row is None:
        return None
    if not verify_password(password, row["password_hash"], row["salt"]):
        return None
    return dict(row)


def set_password(user_id: int, new_password: str, clear_must_change: bool = True) -> None:
    pw_hash, salt = hash_password(new_password)
    db.query(
        "UPDATE users SET password_hash = %s, salt = %s, must_change_password = %s WHERE id = %s",
        (pw_hash, salt, not clear_must_change, user_id),
        commit=True,
    )


def generate_password(length: int = 10) -> str:
    """Generate a readable one-time password (letters + digits)."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_token() -> str:
    """Generate an opaque session token for the persistent login cookie."""
    return secrets.token_urlsafe(32)


def generate_username(prefix: str) -> str:
    """Generate a unique username with the given prefix, e.g. patient-3f9a2b."""
    while True:
        candidate = f"{prefix}-{secrets.token_hex(3)}"
        exists = db.query(
            "SELECT 1 FROM users WHERE username = %s", (candidate,), fetch="one"
        )
        if exists is None:
            return candidate
