"""Snapshot support: capture and restore named vault snapshots."""

import json
import time
from pathlib import Path

_SNAPSHOTS_FILE = "snapshots.json"


def _snapshots_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _SNAPSHOTS_FILE


def _load_snapshots(vault_dir: str) -> dict:
    path = _snapshots_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_snapshots(vault_dir: str, data: dict) -> None:
    path = _snapshots_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def create_snapshot(vault_dir: str, name: str, store: dict) -> dict:
    """Save a named snapshot of the current vault store."""
    snapshots = _load_snapshots(vault_dir)
    entry = {
        "name": name,
        "timestamp": time.time(),
        "store": dict(store),
    }
    snapshots[name] = entry
    _save_snapshots(vault_dir, snapshots)
    return entry


def restore_snapshot(vault_dir: str, name: str) -> dict:
    """Return the store dict from a named snapshot, or None if not found."""
    snapshots = _load_snapshots(vault_dir)
    entry = snapshots.get(name)
    if entry is None:
        return None
    return dict(entry["store"])


def delete_snapshot(vault_dir: str, name: str) -> bool:
    """Delete a named snapshot. Returns True if it existed."""
    snapshots = _load_snapshots(vault_dir)
    if name not in snapshots:
        return False
    del snapshots[name]
    _save_snapshots(vault_dir, snapshots)
    return True


def list_snapshots(vault_dir: str) -> list:
    """Return a list of snapshot metadata dicts (name + timestamp), sorted by time."""
    snapshots = _load_snapshots(vault_dir)
    result = [
        {"name": v["name"], "timestamp": v["timestamp"]}
        for v in snapshots.values()
    ]
    return sorted(result, key=lambda x: x["timestamp"])


def snapshot_summary(vault_dir: str) -> str:
    """Return a human-readable summary of all snapshots."""
    entries = list_snapshots(vault_dir)
    if not entries:
        return "No snapshots found."
    lines = []
    for e in entries:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e["timestamp"]))
        lines.append(f"  {e['name']:30s}  {ts}")
    return "\n".join(lines)
