"""CLI commands for managing webhooks in envault."""

import argparse
import json
from urllib.request import urlopen, Request
from urllib.error import URLError

from .webhook import register_webhook, remove_webhook, list_webhooks, fire_webhook


def cmd_webhook_add(args, vault):
    """Register a new webhook URL for vault events."""
    events = args.events.split(",") if args.events else ["*"]
    register_webhook(vault.vault_dir, args.url, events=events, label=args.label)
    label_str = f" ({args.label})" if args.label else ""
    print(f"Webhook registered{label_str}: {args.url}")
    print(f"Listening for events: {', '.join(events)}")


def cmd_webhook_remove(args, vault):
    """Remove a registered webhook by URL."""
    removed = remove_webhook(vault.vault_dir, args.url)
    if removed:
        print(f"Webhook removed: {args.url}")
    else:
        print(f"No webhook found for: {args.url}")


def cmd_webhook_list(args, vault):
    """List all registered webhooks."""
    hooks = list_webhooks(vault.vault_dir)
    if not hooks:
        print("No webhooks registered.")
        return
    print(f"{'URL':<45} {'Label':<20} Events")
    print("-" * 80)
    for hook in hooks:
        label = hook.get("label") or ""
        events = ", ".join(hook.get("events", ["*"]))
        print(f"{hook['url']:<45} {label:<20} {events}")


def cmd_webhook_test(args, vault):
    """Send a test ping payload to a registered webhook."""
    hooks = list_webhooks(vault.vault_dir)
    target = next((h for h in hooks if h["url"] == args.url), None)
    if target is None:
        print(f"No webhook registered for: {args.url}")
        return

    payload = json.dumps({
        "event": "test",
        "source": "envault",
        "message": "This is a test ping from envault."
    }).encode("utf-8")

    req = Request(
        args.url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=5) as resp:
            print(f"Test ping sent to {args.url} — HTTP {resp.status}")
    except URLError as exc:
        print(f"Failed to reach {args.url}: {exc.reason}")


def register_webhook_commands(subparsers):
    """Attach webhook sub-commands to the provided subparsers object."""
    # webhook add
    p_add = subparsers.add_parser("webhook-add", help="Register a webhook URL")
    p_add.add_argument("url", help="Webhook endpoint URL")
    p_add.add_argument("--events", default=None,
                       help="Comma-separated list of events (default: all)")
    p_add.add_argument("--label", default=None, help="Optional human-readable label")
    p_add.set_defaults(func=cmd_webhook_add)

    # webhook remove
    p_rm = subparsers.add_parser("webhook-remove", help="Remove a registered webhook")
    p_rm.add_argument("url", help="Webhook endpoint URL to remove")
    p_rm.set_defaults(func=cmd_webhook_remove)

    # webhook list
    p_ls = subparsers.add_parser("webhook-list", help="List all registered webhooks")
    p_ls.set_defaults(func=cmd_webhook_list)

    # webhook test
    p_test = subparsers.add_parser("webhook-test", help="Send a test ping to a webhook")
    p_test.add_argument("url", help="Webhook endpoint URL to test")
    p_test.set_defaults(func=cmd_webhook_test)
