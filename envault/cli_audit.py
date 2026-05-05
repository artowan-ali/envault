"""CLI commands for audit log inspection."""

import argparse
from pathlib import Path

from envault.audit import get_log, get_log_for_key, format_log


def cmd_audit_log(args: argparse.Namespace) -> None:
    """Print the audit log, optionally filtered by key."""
    vault_dir = Path(args.vault_dir)
    if not vault_dir.exists():
        print(f"Vault directory not found: {vault_dir}")
        return

    if args.key:
        entries = get_log_for_key(vault_dir, args.key)
        if not entries:
            print(f"No audit entries found for key: {args.key}")
            return
    else:
        entries = get_log(vault_dir)

    print(format_log(entries))


def register_audit_commands(subparsers) -> None:
    """Register audit subcommands on the given subparsers object."""
    audit_parser = subparsers.add_parser(
        "audit",
        help="Show audit log of vault operations",
    )
    audit_parser.add_argument(
        "--vault-dir",
        default=".",
        help="Path to the vault directory (default: current directory)",
    )
    audit_parser.add_argument(
        "--key",
        default=None,
        help="Filter log by a specific key name",
    )
    audit_parser.set_defaults(func=cmd_audit_log)
