"""TTL (time-to-live) support for vault entries."""

import json
import time
from pathlib import Path
from typing import Optional

TTL_FILE = ".envault_ttl.json"


def _load_ttl(vault_dir: Path) -> dict:
    ttl_path = vault_dir / TTL_FILE
    if not ttl_path.exists():
        return {}
    with open(ttl_path, "r") as f:
        return json.load(f)


def _save_ttl(vault_dir: Path, data: dict) -> None:
    ttl_path = vault_dir / TTL_FILE
    with open(ttl_path, "w") as f:
        json.dump(data, f, indent=2)


def set_ttl(vault_dir: Path, key: str, seconds: int) -> None:
    """Set an expiry time for a vault key (Unix timestamp)."""
    data = _load_ttl(vault_dir)
    data[key] = time.time() + seconds
    _save_ttl(vault_dir, data)


def remove_ttl(vault_dir: Path, key: str) -> None:
    """Remove TTL for a key."""
    data = _load_ttl(vault_dir)
    data.pop(key, None)
    _save_ttl(vault_dir, data)


def get_expiry(vault_dir: Path, key: str) -> Optional[float]:
    """Return the expiry timestamp for a key, or None if not set."""
    data = _load_ttl(vault_dir)
    return data.get(key)


def is_expired(vault_dir: Path, key: str) -> bool:
    """Return True if the key has an expired TTL."""
    expiry = get_expiry(vault_dir, key)
    if expiry is None:
        return False
    return time.time() > expiry


def purge_expired(vault_dir: Path) -> list:
    """Return list of keys whose TTL has expired."""
    data = _load_ttl(vault_dir)
    now = time.time()
    expired = [key for key, exp in data.items() if now > exp]
    return expired


def ttl_summary(vault_dir: Path) -> list:
    """Return list of dicts with key, expiry, and remaining seconds."""
    data = _load_ttl(vault_dir)
    now = time.time()
    result = []
    for key, expiry in data.items():
        remaining = max(0.0, expiry - now)
        result.append({"key": key, "expiry": expiry, "remaining": remaining})
    return result
