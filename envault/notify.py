"""Notification dispatch for vault events."""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from envault.webhook import list_webhooks


def _matches_event(webhook_events: list, event: str) -> bool:
    """Check if a webhook should fire for the given event."""
    return "*" in webhook_events or event in webhook_events


def _post_webhook(url: str, payload: dict, timeout: int = 5) -> bool:
    """Send a JSON POST request to a webhook URL. Returns True on success."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except (urllib.error.URLError, OSError):
        return False


def dispatch_event(
    vault_dir: str,
    event: str,
    metadata: Optional[dict] = None,
) -> dict:
    """Dispatch an event to all matching registered webhooks.

    Returns a summary dict with counts of successes and failures.
    """
    webhooks = list_webhooks(vault_dir)
    if metadata is None:
        metadata = {}

    payload = {"event": event, "vault": str(vault_dir), **metadata}

    successes = 0
    failures = 0
    skipped = 0

    for hook in webhooks:
        if not _matches_event(hook.get("events", ["*"]), event):
            skipped += 1
            continue
        ok = _post_webhook(hook["url"], payload)
        if ok:
            successes += 1
        else:
            failures += 1

    return {"event": event, "sent": successes, "failed": failures, "skipped": skipped}
