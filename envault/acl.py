"""Access control list (ACL) management for envault keys."""

import json
from pathlib import Path

ACL_FILE = "acl.json"

VALID_PERMISSIONS = {"read", "write", "delete"}


def _acl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ACL_FILE


def _load_acl(vault_dir: str) -> dict:
    path = _acl_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_acl(vault_dir: str, acl: dict) -> None:
    path = _acl_path(vault_dir)
    with open(path, "w") as f:
        json.dump(acl, f, indent=2)


def set_permission(vault_dir: str, key: str, user: str, permissions: list[str]) -> None:
    """Grant a user specific permissions on a key."""
    invalid = set(permissions) - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}. Valid: {VALID_PERMISSIONS}")
    acl = _load_acl(vault_dir)
    acl.setdefault(key, {})[user] = sorted(set(permissions))
    _save_acl(vault_dir, acl)


def remove_permission(vault_dir: str, key: str, user: str) -> bool:
    """Remove all permissions for a user on a key. Returns True if removed."""
    acl = _load_acl(vault_dir)
    if key in acl and user in acl[key]:
        del acl[key][user]
        if not acl[key]:
            del acl[key]
        _save_acl(vault_dir, acl)
        return True
    return False


def get_permissions(vault_dir: str, key: str, user: str) -> list[str]:
    """Return permissions a user has on a key."""
    acl = _load_acl(vault_dir)
    return acl.get(key, {}).get(user, [])


def has_permission(vault_dir: str, key: str, user: str, permission: str) -> bool:
    """Check if a user has a specific permission on a key."""
    return permission in get_permissions(vault_dir, key, user)


def list_acl(vault_dir: str, key: str) -> dict:
    """Return all user permissions for a given key."""
    acl = _load_acl(vault_dir)
    return acl.get(key, {})


def list_all_acl(vault_dir: str) -> dict:
    """Return the full ACL mapping."""
    return _load_acl(vault_dir)
