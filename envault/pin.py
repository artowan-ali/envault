"""PIN-based quick unlock for envault vaults."""

import hashlib
import json
import os
import time
from pathlib import Path

_PIN_FILE = "pin.json"
_PIN_TTL_SECONDS = 3600  # 1 hour session


def _pin_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _PIN_FILE


def _hash_pin(pin: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{pin}".encode()).hexdigest()


def set_pin(vault_dir: str, pin: str) -> None:
    """Store a hashed PIN for quick unlock."""
    salt = os.urandom(16).hex()
    data = {
        "salt": salt,
        "hash": _hash_pin(pin, salt),
        "created_at": time.time(),
    }
    with open(_pin_path(vault_dir), "w") as f:
        json.dump(data, f)


def verify_pin(vault_dir: str, pin: str) -> bool:
    """Return True if the PIN matches and has not expired."""
    path = _pin_path(vault_dir)
    if not path.exists():
        return False
    with open(path) as f:
        data = json.load(f)
    age = time.time() - data.get("created_at", 0)
    if age > _PIN_TTL_SECONDS:
        return False
    return _hash_pin(pin, data["salt"]) == data["hash"]


def remove_pin(vault_dir: str) -> bool:
    """Remove the stored PIN. Returns True if a PIN existed."""
    path = _pin_path(vault_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def pin_status(vault_dir: str) -> dict:
    """Return info about the current PIN state."""
    path = _pin_path(vault_dir)
    if not path.exists():
        return {"set": False}
    with open(path) as f:
        data = json.load(f)
    age = time.time() - data.get("created_at", 0)
    expired = age > _PIN_TTL_SECONDS
    return {
        "set": True,
        "expired": expired,
        "age_seconds": int(age),
        "ttl_seconds": _PIN_TTL_SECONDS,
    }
