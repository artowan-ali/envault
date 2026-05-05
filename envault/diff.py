"""Git-compatible diff support for sharing encrypted vault changes."""

import json
from typing import Optional


def generate_diff(old_data: dict, new_data: dict) -> dict:
    """Generate a structured diff between two vault states.

    Returns a dict with 'added', 'removed', and 'modified' keys.
    Values are always encrypted blobs (never plaintext).
    """
    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())

    added = {k: new_data[k] for k in new_keys - old_keys}
    removed = {k: old_data[k] for k in old_keys - new_keys}
    modified = {
        k: {"old": old_data[k], "new": new_data[k]}
        for k in old_keys & new_keys
        if old_data[k] != new_data[k]
    }

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
    }


def apply_diff(base_data: dict, diff: dict) -> dict:
    """Apply a diff to a base vault state, returning the new state."""
    result = dict(base_data)

    for key in diff.get("removed", {}):
        result.pop(key, None)

    for key, value in diff.get("added", {}).items():
        result[key] = value

    for key, change in diff.get("modified", {}).items():
        result[key] = change["new"]

    return result


def serialize_diff(diff: dict) -> str:
    """Serialize a diff to a JSON string for storage or transmission."""
    return json.dumps(diff, indent=2, sort_keys=True)


def deserialize_diff(diff_str: str) -> dict:
    """Deserialize a diff from a JSON string."""
    data = json.loads(diff_str)
    for required_key in ("added", "removed", "modified"):
        if required_key not in data:
            raise ValueError(f"Invalid diff format: missing '{required_key}' key")
    return data


def diff_summary(diff: dict) -> str:
    """Return a human-readable summary of a diff."""
    added = len(diff.get("added", {}))
    removed = len(diff.get("removed", {}))
    modified = len(diff.get("modified", {}))
    parts = []
    if added:
        parts.append(f"+{added} added")
    if removed:
        parts.append(f"-{removed} removed")
    if modified:
        parts.append(f"~{modified} modified")
    return ", ".join(parts) if parts else "no changes"
