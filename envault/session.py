"""Session management: cache the unlocked vault password for a TTL period."""

import json
import os
import time
from pathlib import Path

DEFAULT_SESSION_TTL = 900  # 15 minutes


def _session_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".session"


def _load_session(vault_dir: str) -> dict:
    path = _session_path(vault_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_session(vault_dir: str, data: dict) -> None:
    path = _session_path(vault_dir)
    path.write_text(json.dumps(data))
    # Restrict permissions to owner only
    os.chmod(path, 0o600)


def save_session(vault_dir: str, password: str, ttl: int = DEFAULT_SESSION_TTL) -> None:
    """Persist the password in the session cache with an expiry timestamp."""
    data = {
        "password": password,
        "expires_at": time.time() + ttl,
    }
    _save_session(vault_dir, data)


def load_session(vault_dir: str) -> str | None:
    """Return the cached password if the session is still valid, else None."""
    data = _load_session(vault_dir)
    if not data:
        return None
    if time.time() > data.get("expires_at", 0):
        clear_session(vault_dir)
        return None
    return data.get("password")


def clear_session(vault_dir: str) -> None:
    """Delete the session cache file."""
    path = _session_path(vault_dir)
    if path.exists():
        path.unlink()


def session_status(vault_dir: str) -> dict:
    """Return a dict describing the current session state."""
    data = _load_session(vault_dir)
    if not data:
        return {"active": False, "expires_at": None, "remaining_seconds": None}
    remaining = data.get("expires_at", 0) - time.time()
    if remaining <= 0:
        clear_session(vault_dir)
        return {"active": False, "expires_at": None, "remaining_seconds": None}
    return {
        "active": True,
        "expires_at": data["expires_at"],
        "remaining_seconds": int(remaining),
    }
