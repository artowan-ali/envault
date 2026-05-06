"""Tag management for vault entries — group and filter keys by tag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

TAGS_FILENAME = "tags.json"


def _load_tags(vault_dir: str) -> Dict[str, List[str]]:
    """Load the tags mapping {key: [tag, ...]} from disk."""
    path = Path(vault_dir) / TAGS_FILENAME
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_tags(vault_dir: str, tags: Dict[str, List[str]]) -> None:
    """Persist the tags mapping to disk."""
    path = Path(vault_dir) / TAGS_FILENAME
    with path.open("w") as fh:
        json.dump(tags, fh, indent=2, sort_keys=True)


def add_tag(vault_dir: str, key: str, tag: str) -> None:
    """Add *tag* to the list of tags for *key*."""
    tags = _load_tags(vault_dir)
    entry = tags.setdefault(key, [])
    if tag not in entry:
        entry.append(tag)
        entry.sort()
    _save_tags(vault_dir, tags)


def remove_tag(vault_dir: str, key: str, tag: str) -> bool:
    """Remove *tag* from *key*. Returns True if the tag existed."""
    tags = _load_tags(vault_dir)
    entry = tags.get(key, [])
    if tag not in entry:
        return False
    entry.remove(tag)
    if not entry:
        del tags[key]
    _save_tags(vault_dir, tags)
    return True


def get_tags(vault_dir: str, key: str) -> List[str]:
    """Return all tags associated with *key*."""
    return _load_tags(vault_dir).get(key, [])


def keys_for_tag(vault_dir: str, tag: str) -> List[str]:
    """Return all keys that carry *tag*."""
    tags = _load_tags(vault_dir)
    return sorted(k for k, tlist in tags.items() if tag in tlist)


def all_tags(vault_dir: str) -> List[str]:
    """Return a sorted, deduplicated list of every tag in the vault."""
    tags = _load_tags(vault_dir)
    seen: set = set()
    for tlist in tags.values():
        seen.update(tlist)
    return sorted(seen)


def tags_summary(vault_dir: str) -> str:
    """Return a human-readable summary of tag usage."""
    tags = _load_tags(vault_dir)
    if not tags:
        return "No tags defined."
    lines = []
    for key in sorted(tags):
        lines.append(f"  {key}: {', '.join(tags[key])}")
    return "\n".join(lines)
