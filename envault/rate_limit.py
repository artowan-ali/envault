"""Rate limiting for vault operations."""

import json
import time
from pathlib import Path

_RATE_LIMIT_FILE = "rate_limits.json"


def _rl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _RATE_LIMIT_FILE


def _load_rl(vault_dir: str) -> dict:
    path = _rl_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_rl(vault_dir: str, data: dict) -> None:
    with open(_rl_path(vault_dir), "w") as f:
        json.dump(data, f, indent=2)


def set_rate_limit(vault_dir: str, operation: str, max_calls: int, window_seconds: int) -> dict:
    """Configure a rate limit for a named operation."""
    data = _load_rl(vault_dir)
    data[operation] = {
        "max_calls": max_calls,
        "window_seconds": window_seconds,
        "calls": []
    }
    _save_rl(vault_dir, data)
    return data[operation]


def remove_rate_limit(vault_dir: str, operation: str) -> bool:
    """Remove rate limit config for an operation. Returns True if removed."""
    data = _load_rl(vault_dir)
    if operation not in data:
        return False
    del data[operation]
    _save_rl(vault_dir, data)
    return True


def check_rate_limit(vault_dir: str, operation: str) -> tuple[bool, int]:
    """Check if operation is allowed. Returns (allowed, retry_after_seconds)."""
    data = _load_rl(vault_dir)
    if operation not in data:
        return True, 0

    entry = data[operation]
    now = time.time()
    window = entry["window_seconds"]
    max_calls = entry["max_calls"]

    # Prune old calls outside the window
    entry["calls"] = [t for t in entry["calls"] if now - t < window]

    if len(entry["calls"]) >= max_calls:
        oldest = min(entry["calls"])
        retry_after = int(window - (now - oldest)) + 1
        _save_rl(vault_dir, data)
        return False, retry_after

    entry["calls"].append(now)
    _save_rl(vault_dir, data)
    return True, 0


def get_rate_limit(vault_dir: str, operation: str) -> dict | None:
    """Return the rate limit config for an operation, or None."""
    return _load_rl(vault_dir).get(operation)


def list_rate_limits(vault_dir: str) -> dict:
    """Return all configured rate limits."""
    return _load_rl(vault_dir)


def reset_calls(vault_dir: str, operation: str) -> bool:
    """Reset call history for an operation. Returns True if reset."""
    data = _load_rl(vault_dir)
    if operation not in data:
        return False
    data[operation]["calls"] = []
    _save_rl(vault_dir, data)
    return True
