"""CLI commands for value history management."""

import argparse
import time
from pathlib import Path

from envault.history import get_history, clear_history, list_keys_with_history
from envault.vault import Vault
from envault.cli import get_password


def cmd_history_show(args: argparse.Namespace) -> None:
    """Show decrypted value history for a key."""
    vault_dir = Path(args.vault_dir)
    password = get_password(args)
    vault = Vault(vault_dir, password)
    entries = get_history(vault_dir, args.key)
    if not entries:
        print(f"No history found for key: {args.key}")
        return
    print(f"History for '{args.key}' ({len(entries)} entries):")
    for i, entry in enumerate(entries, 1):
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["timestamp"]))
        try:
            value = vault._decrypt_value(entry["value"])
        except Exception:
            value = "<decryption failed>"
        note = f"  [{entry['note']}]" if entry.get("note") else ""
        print(f"  {i:3}. {ts}  {value}{note}")


def cmd_history_clear(args: argparse.Namespace) -> None:
    """Clear history for a specific key."""
    vault_dir = Path(args.vault_dir)
    removed = clear_history(vault_dir, args.key)
    if removed:
        print(f"Cleared {removed} history entries for '{args.key}'.")
    else:
        print(f"No history to clear for '{args.key}'.")


def cmd_history_list(args: argparse.Namespace) -> None:
    """List all keys that have history entries."""
    vault_dir = Path(args.vault_dir)
    keys = list_keys_with_history(vault_dir)
    if not keys:
        print("No history recorded yet.")
        return
    print("Keys with history:")
    for key in sorted(keys):
        entries = get_history(vault_dir, key)
        print(f"  {key}  ({len(entries)} entries)")


def register_history_commands(subparsers, parent_parser) -> None:
    hist = subparsers.add_parser("history", help="Value history commands")
    hist_sub = hist.add_subparsers(dest="history_cmd")

    show_p = hist_sub.add_parser("show", parents=[parent_parser], help="Show history for a key")
    show_p.add_argument("key", help="Key name")
    show_p.set_defaults(func=cmd_history_show)

    clear_p = hist_sub.add_parser("clear", parents=[parent_parser], help="Clear history for a key")
    clear_p.add_argument("key", help="Key name")
    clear_p.set_defaults(func=cmd_history_clear)

    list_p = hist_sub.add_parser("list", parents=[parent_parser], help="List keys with history")
    list_p.set_defaults(func=cmd_history_list)
