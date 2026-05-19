"""Search and filter utilities for vault keys and values."""

import fnmatch
import re
from typing import Optional

from envault.vault import Vault


def search_keys(
    vault: Vault,
    pattern: str,
    *,
    use_regex: bool = False,
) -> list[str]:
    """Return keys matching a glob pattern (or regex if use_regex=True)."""
    all_keys = vault.list_keys()
    if use_regex:
        rx = re.compile(pattern)
        return [k for k in all_keys if rx.search(k)]
    return [k for k in all_keys if fnmatch.fnmatch(k, pattern)]


def search_values(
    vault: Vault,
    substring: str,
    *,
    case_sensitive: bool = True,
) -> list[tuple[str, str]]:
    """Return (key, value) pairs where value contains the substring."""
    results = []
    for key in vault.list_keys():
        value = vault.get(key) or ""
        haystack = value if case_sensitive else value.lower()
        needle = substring if case_sensitive else substring.lower()
        if needle in haystack:
            results.append((key, value))
    return results


def filter_by_prefix(vault: Vault, prefix: str) -> list[str]:
    """Return keys that start with the given prefix."""
    return [k for k in vault.list_keys() if k.startswith(prefix)]


def filter_by_suffix(vault: Vault, suffix: str) -> list[str]:
    """Return keys that end with the given suffix."""
    return [k for k in vault.list_keys() if k.endswith(suffix)]


def search_summary(
    vault: Vault,
    pattern: str,
    *,
    use_regex: bool = False,
) -> dict:
    """Return a summary dict with matched keys and count."""
    matched = search_keys(vault, pattern, use_regex=use_regex)
    return {
        "pattern": pattern,
        "use_regex": use_regex,
        "count": len(matched),
        "keys": matched,
    }
