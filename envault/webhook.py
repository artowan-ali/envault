"""Webhook notification support for envault vault events."""

import json
import urllib.request
import urllib.error
from pathlib import Path

_WEBHOOK_FILE = "webhooks.json"


def _load_webhooks(vault_dir: str) -> dict:
    path = Path(vault_dir) / _WEBHOOK_FILE
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_webhooks(vault_dir: str, data: dict) -> None:
    path = Path(vault_dir) / _WEBHOOK_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def register_webhook(vault_dir: str, name: str, url: str, events: list[str] | None = None) -> None:
    """Register a webhook URL for the given event types."""
    data = _load_webhooks(vault_dir)
    data[name] = {"url": url, "events": events or ["*"]}
    _save_webhooks(vault_dir, data)


def remove_webhook(vault_dir: str, name: str) -> bool:
    """Remove a registered webhook. Returns True if it existed."""
    data = _load_webhooks(vault_dir)
    if name not in data:
        return False
    del data[name]
    _save_webhooks(vault_dir, data)
    return True


def list_webhooks(vault_dir: str) -> dict:
    """Return all registered webhooks."""
    return _load_webhooks(vault_dir)


def fire_event(vault_dir: str, event: str, payload: dict) -> list[dict]:
    """Send event payload to all matching webhooks. Returns list of results."""
    data = _load_webhooks(vault_dir)
    results = []
    body = json.dumps({"event": event, **payload}).encode()
    for name, cfg in data.items():
        if "*" not in cfg["events"] and event not in cfg["events"]:
            continue
        req = urllib.request.Request(
            cfg["url"],
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append({"name": name, "status": resp.status, "error": None})
        except urllib.error.URLError as e:
            results.append({"name": name, "status": None, "error": str(e)})
    return results
