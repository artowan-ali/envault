"""Notify users of keys approaching or past their TTL expiry."""

import time
from pathlib import Path
from typing import List, Dict, Optional

from envault.ttl import _load_ttl
from envault.notify import dispatch_event


def get_expiring_keys(
    vault_dir: Path,
    within_seconds: int = 86400,
) -> List[Dict]:
    """Return keys expiring within the given window (default: 24 hours)."""
    ttl_data = _load_ttl(vault_dir)
    now = time.time()
    results = []
    for key, expiry in ttl_data.items():
        time_left = expiry - now
        if time_left <= within_seconds:
            results.append({
                "key": key,
                "expiry": expiry,
                "time_left": time_left,
                "expired": time_left < 0,
            })
    results.sort(key=lambda x: x["expiry"])
    return results


def get_expired_keys(vault_dir: Path) -> List[Dict]:
    """Return all keys that have already expired."""
    return [e for e in get_expiring_keys(vault_dir, within_seconds=0) if e["expired"]]


def notify_expiring_keys(
    vault_dir: Path,
    within_seconds: int = 86400,
    webhooks: Optional[List[Dict]] = None,
) -> List[Dict]:
    """Dispatch webhook events for keys expiring soon or already expired.

    Returns the list of affected key entries.
    """
    expiring = get_expiring_keys(vault_dir, within_seconds=within_seconds)
    for entry in expiring:
        event = "key.expired" if entry["expired"] else "key.expiring"
        payload = {
            "key": entry["key"],
            "expiry": entry["expiry"],
            "time_left": entry["time_left"],
        }
        dispatch_event(vault_dir, event, payload, webhooks=webhooks)
    return expiring


def expiry_summary(entries: List[Dict]) -> str:
    """Return a human-readable summary of expiring/expired keys."""
    if not entries:
        return "No keys are expiring soon."
    lines = []
    for e in entries:
        if e["expired"]:
            ago = abs(e["time_left"])
            lines.append(f"  {e['key']}: EXPIRED {ago:.0f}s ago")
        else:
            lines.append(f"  {e['key']}: expires in {e['time_left']:.0f}s")
    return "\n".join(lines)
