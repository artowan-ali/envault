"""CLI commands for managing webhooks in envault."""

import argparse
from envault.webhook import register_webhook, remove_webhook, list_webhooks, fire_event


def cmd_webhook_add(args: argparse.Namespace) -> None:
    events = args.events.split(",") if args.events else ["*"]
    register_webhook(args.vault_dir, args.name, args.url, events)
    print(f"Webhook '{args.name}' registered for events: {', '.join(events)}")


def cmd_webhook_remove(args: argparse.Namespace) -> None:
    removed = remove_webhook(args.vault_dir, args.name)
    if removed:
        print(f"Webhook '{args.name}' removed.")
    else:
        print(f"No webhook named '{args.name}' found.")


def cmd_webhook_list(args: argparse.Namespace) -> None:
    hooks = list_webhooks(args.vault_dir)
    if not hooks:
        print("No webhooks registered.")
        return
    for name, cfg in hooks.items():
        events = ", ".join(cfg["events"])
        print(f"  {name}: {cfg['url']} [{events}]")


def cmd_webhook_test(args: argparse.Namespace) -> None:
    results = fire_event(args.vault_dir, "test", {"message": "envault webhook test"})
    if not results:
        print("No webhooks matched event 'test'.")
        return
    for r in results:
        if r["error"]:
            print(f"  {r['name']}: FAILED — {r['error']}")
        else:
            print(f"  {r['name']}: OK (HTTP {r['status']})")


def register_webhook_commands(subparsers, parent_kwargs: dict) -> None:
    wp = subparsers.add_parser("webhook", help="Manage webhook notifications")
    ws = wp.add_subparsers(dest="webhook_cmd")

    p_add = ws.add_parser("add", **parent_kwargs)
    p_add.add_argument("name", help="Webhook name")
    p_add.add_argument("url", help="Webhook URL")
    p_add.add_argument("--events", help="Comma-separated event names (default: *)")
    p_add.set_defaults(func=cmd_webhook_add)

    p_rm = ws.add_parser("remove", **parent_kwargs)
    p_rm.add_argument("name", help="Webhook name")
    p_rm.set_defaults(func=cmd_webhook_remove)

    p_ls = ws.add_parser("list", **parent_kwargs)
    p_ls.set_defaults(func=cmd_webhook_list)

    p_test = ws.add_parser("test", **parent_kwargs)
    p_test.set_defaults(func=cmd_webhook_test)
