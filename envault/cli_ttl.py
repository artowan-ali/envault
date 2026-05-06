"""CLI commands for TTL management."""

import argparse
from pathlib import Path

from envault.ttl import set_ttl, remove_ttl, get_expiry, purge_expired, ttl_summary, is_expired
from envault.vault import Vault


def cmd_ttl_set(args: argparse.Namespace) -> None:
    """Set a TTL on a vault key."""
    vault_dir = Path(args.vault_dir)
    vault = Vault(vault_dir, args.password)
    if vault.get(args.key) is None:
        print(f"Key '{args.key}' not found in vault.")
        return
    set_ttl(vault_dir, args.key, args.seconds)
    print(f"TTL set: '{args.key}' expires in {args.seconds}s.")


def cmd_ttl_remove(args: argparse.Namespace) -> None:
    """Remove TTL from a vault key."""
    vault_dir = Path(args.vault_dir)
    remove_ttl(vault_dir, args.key)
    print(f"TTL removed from '{args.key}'.")


def cmd_ttl_list(args: argparse.Namespace) -> None:
    """List all keys with TTL info."""
    vault_dir = Path(args.vault_dir)
    entries = ttl_summary(vault_dir)
    if not entries:
        print("No TTL entries found.")
        return
    for entry in entries:
        status = "EXPIRED" if entry["remaining"] == 0.0 else f"{entry['remaining']:.1f}s remaining"
        print(f"  {entry['key']}: {status}")


def cmd_ttl_purge(args: argparse.Namespace) -> None:
    """Delete expired keys from the vault."""
    vault_dir = Path(args.vault_dir)
    vault = Vault(vault_dir, args.password)
    expired = purge_expired(vault_dir)
    if not expired:
        print("No expired keys to purge.")
        return
    for key in expired:
        vault.delete(key)
        remove_ttl(vault_dir, key)
        print(f"Purged expired key: '{key}'")


def register_ttl_commands(subparsers, common_args_fn) -> None:
    p_set = subparsers.add_parser("ttl-set", help="Set TTL for a key")
    common_args_fn(p_set)
    p_set.add_argument("key", help="Key name")
    p_set.add_argument("seconds", type=int, help="TTL in seconds")
    p_set.set_defaults(func=cmd_ttl_set)

    p_rm = subparsers.add_parser("ttl-remove", help="Remove TTL from a key")
    common_args_fn(p_rm)
    p_rm.add_argument("key", help="Key name")
    p_rm.set_defaults(func=cmd_ttl_remove)

    p_list = subparsers.add_parser("ttl-list", help="List TTL entries")
    common_args_fn(p_list)
    p_list.set_defaults(func=cmd_ttl_list)

    p_purge = subparsers.add_parser("ttl-purge", help="Purge expired keys")
    common_args_fn(p_purge)
    p_purge.set_defaults(func=cmd_ttl_purge)
