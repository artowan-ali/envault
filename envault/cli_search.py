"""CLI commands for searching vault entries."""

import argparse
import sys

from envault.vault import Vault
from envault.cli import get_password
from envault.search import search_keys, search_values, filter_by_prefix, search_summary


def cmd_search(args: argparse.Namespace) -> None:
    """Search vault entries by key name or value pattern."""
    password = get_password(confirm=False)
    vault = Vault(args.vault_dir, password)

    all_entries = {k: vault.get(k) for k in vault.list_keys()}

    use_regex = getattr(args, "regex", False)

    if args.target == "values":
        matched = search_values(all_entries, args.pattern, use_regex=use_regex)
    elif args.target == "prefix":
        filtered = filter_by_prefix(all_entries, args.pattern)
        matched = sorted(filtered.keys())
    else:
        matched = search_keys(all_entries, args.pattern, use_regex=use_regex)

    summary = search_summary(matched, args.pattern, target=args.target or "keys")
    print(summary)

    for key in matched:
        if args.show_values:
            print(f"  {key}={all_entries[key]}")
        else:
            print(f"  {key}")


def register_search_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register search subcommand."""
    p = subparsers.add_parser("search", help="Search vault entries")
    p.add_argument("pattern", help="Glob or regex pattern to search")
    p.add_argument(
        "--target",
        choices=["keys", "values", "prefix"],
        default="keys",
        help="What to search: keys (default), values, or prefix",
    )
    p.add_argument(
        "--regex",
        action="store_true",
        default=False,
        help="Treat pattern as a regular expression",
    )
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Display values alongside matched keys",
    )
    p.add_argument("--vault-dir", default=".envault")
    p.set_defaults(func=cmd_search)
