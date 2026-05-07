"""Vault locking mechanism to prevent concurrent access."""

import os
import time
import json
from pathlib import Path

LOCK_FILENAME = ".vault.lock"
LOCK_TIMEOUT = 30  # seconds


def _lock_path(vault_dir: str) -> Path:
    return Path(vault_dir) / LOCK_FILENAME


def acquire_lock(vault_dir: str, owner: str = None) -> bool:
    """Attempt to acquire a lock on the vault directory.

    Returns True if lock was acquired, False if vault is already locked.
    """
    lock_file = _lock_path(vault_dir)

    if lock_file.exists():
        try:
            data = json.loads(lock_file.read_text())
            acquired_at = data.get("acquired_at", 0)
            if time.time() - acquired_at < LOCK_TIMEOUT:
                return False
            # Stale lock — remove it
            lock_file.unlink()
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable lock file — remove it
            try:
                lock_file.unlink()
            except OSError:
                pass

    payload = {
        "owner": owner or str(os.getpid()),
        "acquired_at": time.time(),
    }
    lock_file.write_text(json.dumps(payload))
    return True


def release_lock(vault_dir: str) -> bool:
    """Release the vault lock. Returns True if lock was removed."""
    lock_file = _lock_path(vault_dir)
    if lock_file.exists():
        lock_file.unlink()
        return True
    return False


def is_locked(vault_dir: str) -> bool:
    """Return True if the vault is currently locked (and lock is not stale)."""
    lock_file = _lock_path(vault_dir)
    if not lock_file.exists():
        return False
    try:
        data = json.loads(lock_file.read_text())
        acquired_at = data.get("acquired_at", 0)
        return time.time() - acquired_at < LOCK_TIMEOUT
    except (json.JSONDecodeError, OSError):
        return False


def lock_info(vault_dir: str) -> dict:
    """Return lock metadata, or empty dict if not locked."""
    lock_file = _lock_path(vault_dir)
    if not lock_file.exists():
        return {}
    try:
        return json.loads(lock_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
