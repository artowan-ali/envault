"""Search and filter vault entries by key name or value pattern."""

import fnmatch
import re
from typing import Dict, List, Optional


def search_keys(
    entries: Dict[str, str],
    pattern: str,
    use_regex: bool = False,
) -> List[str]:
    """Return keys matching the given glob or regex pattern."""
    matched = []
    for key in entries:
        if use_regex:
            if re.search(pattern, key):
                matched.append(key)
        else:
            if fnmatch.fnmatch(key, pattern):
                matched.append(key)
    return sorted(matched)


def search_values(
    entries: Dict[str, str],
    pattern: str,
    use_regex: bool = False,
) -> List[str]:
    """Return keys whose values match the given glob or regex pattern."""
    matched = []
    for key, value in entries.items():
        if use_regex:
            if re.search(pattern, value):
                matched.append(key)
        else:
            if fnmatch.fnmatch(value, pattern):
                matched.append(key)
    return sorted(matched)


def filter_by_prefix(entries: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return a dict of entries whose keys start with the given prefix."""
    return {k: v for k, v in entries.items() if k.startswith(prefix)}


def filter_by_suffix(entries: Dict[str, str], suffix: str) -> Dict[str, str]:
    """Return a dict of entries whose keys end with the given suffix.

    Args:
        entries: A mapping of key-value pairs to filter.
        suffix: The suffix string to match against each key.

    Returns:
        A new dict containing only entries whose keys end with ``suffix``.
    """
    return {k: v for k, v in entries.items() if k.endswith(suffix)}


def search_summary(
    matched_keys: List[str],
    pattern: str,
    target: str = "keys",
) -> str:
    """Return a human-readable summary of search results."""
    count = len(matched_keys)
    if count == 0:
        return f"No {target} matched pattern '{pattern}'."
    noun = "entry" if count == 1 else "entries"
    return f"{count} {noun} matched pattern '{pattern}' in {target}."
