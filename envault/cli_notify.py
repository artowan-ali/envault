"""CLI commands for testing and inspecting notification dispatch."""

import argparse
from envault.notify import dispatch_event
from envault.webhook import list_webhooks


def cmd_notify_test(args):
    """Manually fire a test notification event to all matching webhooks."""
    result = dispatch_event(
        args.vault_dir,
        event=args.event,
        metadata={"source": "manual-test"},
    )
    print(f"Event     : {result['event']}")
    print(f"Sent      : {result['sent']}")
    print(f"Failed    : {result['failed']}")
    print(f"Skipped   : {result['skipped']}")
    if result["failed"] > 0:
        print("[warn] Some webhooks failed to receive the event.")


def cmd_notify_preview(args):
    """Preview which webhooks would fire for a given event (dry-run)."""
    webhooks = list_webhooks(args.vault_dir)
    if not webhooks:
        print("No webhooks registered.")
        return

    print(f"Webhooks that would fire for event '{args.event}':")
    matched = 0
    for hook in webhooks:
        events = hook.get("events", ["*"])
        if "*" in events or args.event in events:
            print(f"  [match]  {hook['name']} -> {hook['url']}  (events: {events})")
            matched += 1
        else:
            print(f"  [skip]   {hook['name']} -> {hook['url']}  (events: {events})")

    print(f"\n{matched}/{len(webhooks)} webhook(s) would fire.")


def register_notify_commands(subparsers, parent_kwargs):
    """Register notify subcommands onto the given subparsers object."""
    notify_p = subparsers.add_parser("notify", help="Notification dispatch tools")
    notify_sub = notify_p.add_subparsers(dest="notify_cmd")

    # notify test
    test_p = notify_sub.add_parser("test", help="Fire a test event to all matching webhooks", **parent_kwargs)
    test_p.add_argument("event", help="Event name to dispatch (e.g. set, delete, rotate)")
    test_p.set_defaults(func=cmd_notify_test)

    # notify preview
    prev_p = notify_sub.add_parser("preview", help="Preview which webhooks would fire (dry-run)", **parent_kwargs)
    prev_p.add_argument("event", help="Event name to preview")
    prev_p.set_defaults(func=cmd_notify_preview)
