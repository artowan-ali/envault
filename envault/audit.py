"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_FILENAME = ".envault_audit.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_log(vault_dir: Path) -> List[dict]:
    log_path = vault_dir / AUDIT_FILENAME
    if not log_path.exists():
        return []
    with open(log_path, "r") as f:
        return json.load(f)


def _save_log(vault_dir: Path, entries: List[dict]) -> None:
    log_path = vault_dir / AUDIT_FILENAME
    with open(log_path, "w") as f:
        json.dump(entries, f, indent=2)


def record_event(vault_dir: Path, action: str, key: str, user: Optional[str] = None) -> None:
    """Append an audit event for the given action and key."""
    entries = _load_log(vault_dir)
    entries.append({
        "timestamp": _timestamp(),
        "action": action,
        "key": key,
        "user": user or os.environ.get("USER", "unknown"),
    })
    _save_log(vault_dir, entries)


def get_log(vault_dir: Path) -> List[dict]:
    """Return all audit log entries."""
    return _load_log(vault_dir)


def get_log_for_key(vault_dir: Path, key: str) -> List[dict]:
    """Return audit log entries filtered by key."""
    return [e for e in _load_log(vault_dir) if e["key"] == key]


def format_log(entries: List[dict]) -> str:
    """Return a human-readable string of audit entries."""
    if not entries:
        return "No audit entries found."
    lines = []
    for e in entries:
        user = e.get("user", "unknown")
        lines.append(f"[{e['timestamp']}] {e['action'].upper():8s} key={e['key']} user={user}")
    return "\n".join(lines)
