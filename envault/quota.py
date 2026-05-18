"""Quota management: enforce limits on number of keys per vault or namespace."""

import json
from pathlib import Path

DEFAULT_QUOTA_FILE = "quota.json"


def _quota_path(vault_dir: str) -> Path:
    return Path(vault_dir) / DEFAULT_QUOTA_FILE


def _load_quotas(vault_dir: str) -> dict:
    path = _quota_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_quotas(vault_dir: str, quotas: dict) -> None:
    path = _quota_path(vault_dir)
    with open(path, "w") as f:
        json.dump(quotas, f, indent=2)


def set_quota(vault_dir: str, scope: str, limit: int) -> None:
    """Set a maximum key count for a given scope (e.g. 'global' or a namespace)."""
    if limit < 1:
        raise ValueError("Quota limit must be a positive integer.")
    quotas = _load_quotas(vault_dir)
    quotas[scope] = limit
    _save_quotas(vault_dir, quotas)


def remove_quota(vault_dir: str, scope: str) -> bool:
    """Remove a quota for the given scope. Returns True if it existed."""
    quotas = _load_quotas(vault_dir)
    if scope not in quotas:
        return False
    del quotas[scope]
    _save_quotas(vault_dir, quotas)
    return True


def get_quota(vault_dir: str, scope: str) -> int | None:
    """Return the quota limit for a scope, or None if not set."""
    return _load_quotas(vault_dir).get(scope)


def list_quotas(vault_dir: str) -> dict:
    """Return all defined quotas as {scope: limit}."""
    return _load_quotas(vault_dir)


def check_quota(vault_dir: str, scope: str, current_count: int) -> bool:
    """Return True if current_count is within the quota for the scope.

    If no quota is set for the scope, also checks 'global'. If neither
    is set, the check always passes.
    """
    quotas = _load_quotas(vault_dir)
    limit = quotas.get(scope) or quotas.get("global")
    if limit is None:
        return True
    return current_count <= limit


def quota_summary(vault_dir: str) -> str:
    """Return a human-readable summary of all quotas."""
    quotas = _load_quotas(vault_dir)
    if not quotas:
        return "No quotas defined."
    lines = [f"  {scope}: {limit} keys" for scope, limit in sorted(quotas.items())]
    return "Quotas:\n" + "\n".join(lines)
