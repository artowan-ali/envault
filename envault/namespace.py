"""Namespace support for grouping vault keys under logical prefixes."""

import json
from pathlib import Path

_NAMESPACE_FILE = "namespaces.json"


def _load_namespaces(vault_dir: str) -> dict:
    path = Path(vault_dir) / _NAMESPACE_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_namespaces(vault_dir: str, data: dict) -> None:
    path = Path(vault_dir) / _NAMESPACE_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_namespace(vault_dir: str, key: str, namespace: str) -> None:
    """Assign a key to a namespace."""
    data = _load_namespaces(vault_dir)
    data[key] = namespace
    _save_namespaces(vault_dir, data)


def remove_namespace(vault_dir: str, key: str) -> bool:
    """Remove a key's namespace assignment. Returns True if it existed."""
    data = _load_namespaces(vault_dir)
    if key in data:
        del data[key]
        _save_namespaces(vault_dir, data)
        return True
    return False


def get_namespace(vault_dir: str, key: str) -> str | None:
    """Return the namespace for a key, or None if unassigned."""
    return _load_namespaces(vault_dir).get(key)


def list_namespace_keys(vault_dir: str, namespace: str) -> list[str]:
    """Return all keys assigned to a given namespace, sorted."""
    data = _load_namespaces(vault_dir)
    return sorted(k for k, ns in data.items() if ns == namespace)


def list_namespaces(vault_dir: str) -> list[str]:
    """Return all unique namespace names, sorted."""
    data = _load_namespaces(vault_dir)
    return sorted(set(data.values()))


def namespace_summary(vault_dir: str) -> dict:
    """Return a dict mapping each namespace to its list of keys."""
    data = _load_namespaces(vault_dir)
    summary: dict = {}
    for key, ns in data.items():
        summary.setdefault(ns, []).append(key)
    for ns in summary:
        summary[ns].sort()
    return summary
