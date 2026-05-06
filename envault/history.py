"""Value history tracking for envault vault keys."""

import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

HISTORY_FILE = "history.json"
MAX_HISTORY_PER_KEY = 20


def _load_history(vault_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    path = vault_dir / HISTORY_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_history(vault_dir: Path, history: Dict[str, List[Dict[str, Any]]]) -> None:
    path = vault_dir / HISTORY_FILE
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def record_value(vault_dir: Path, key: str, encrypted_value: str, note: str = "") -> None:
    """Append an encrypted value snapshot to a key's history."""
    history = _load_history(vault_dir)
    if key not in history:
        history[key] = []
    entry = {
        "timestamp": time.time(),
        "value": encrypted_value,
        "note": note,
    }
    history[key].append(entry)
    # Trim to max entries
    history[key] = history[key][-MAX_HISTORY_PER_KEY:]
    _save_history(vault_dir, history)


def get_history(vault_dir: Path, key: str) -> List[Dict[str, Any]]:
    """Return the history entries for a given key, oldest first."""
    history = _load_history(vault_dir)
    return history.get(key, [])


def clear_history(vault_dir: Path, key: str) -> int:
    """Remove all history for a key. Returns number of entries removed."""
    history = _load_history(vault_dir)
    removed = len(history.pop(key, []))
    _save_history(vault_dir, history)
    return removed


def list_keys_with_history(vault_dir: Path) -> List[str]:
    """Return all keys that have at least one history entry."""
    history = _load_history(vault_dir)
    return [k for k, v in history.items() if v]


def history_summary(vault_dir: Path, key: str) -> Optional[Dict[str, Any]]:
    """Return a summary dict for a key's history, or None if no history."""
    entries = get_history(vault_dir, key)
    if not entries:
        return None
    return {
        "key": key,
        "count": len(entries),
        "oldest": entries[0]["timestamp"],
        "newest": entries[-1]["timestamp"],
    }
