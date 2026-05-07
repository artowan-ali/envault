"""Alias support: map short names to vault keys."""

import json
from pathlib import Path

_ALIAS_FILE = "aliases.json"


def _load_aliases(vault_dir: str) -> dict:
    path = Path(vault_dir) / _ALIAS_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_aliases(vault_dir: str, aliases: dict) -> None:
    path = Path(vault_dir) / _ALIAS_FILE
    with open(path, "w") as f:
        json.dump(aliases, f, indent=2, sort_keys=True)


def set_alias(vault_dir: str, alias: str, key: str) -> None:
    """Create or update an alias pointing to a vault key."""
    aliases = _load_aliases(vault_dir)
    aliases[alias] = key
    _save_aliases(vault_dir, aliases)


def remove_alias(vault_dir: str, alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(vault_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(vault_dir, aliases)
    return True


def resolve_alias(vault_dir: str, alias: str) -> str | None:
    """Return the vault key for an alias, or None if not found."""
    aliases = _load_aliases(vault_dir)
    return aliases.get(alias)


def list_aliases(vault_dir: str) -> dict:
    """Return all alias -> key mappings."""
    return _load_aliases(vault_dir)


def rename_alias(vault_dir: str, old_alias: str, new_alias: str) -> bool:
    """Rename an alias. Returns True on success, False if old alias not found."""
    aliases = _load_aliases(vault_dir)
    if old_alias not in aliases:
        return False
    aliases[new_alias] = aliases.pop(old_alias)
    _save_aliases(vault_dir, aliases)
    return True
