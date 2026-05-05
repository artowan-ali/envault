"""Command-line interface for envault."""

import sys
import argparse
from pathlib import Path

from envault.vault import Vault
from envault.diff import generate_diff, apply_diff, serialize_diff, deserialize_diff, diff_summary


DEFAULT_VAULT_PATH = ".envault"
DEFAULT_PASSWORD_ENV = "ENVAULT_PASSWORD"


def get_password(args) -> str:
    """Retrieve password from args or prompt user."""
    import os
    if hasattr(args, "password") and args.password:
        return args.password
    password = os.environ.get(DEFAULT_PASSWORD_ENV)
    if password:
        return password
    import getpass
    return getpass.getpass("Vault password: ")


def cmd_set(args):
    password = get_password(args)
    vault = Vault(args.vault, password)
    vault.set(args.key, args.value)
    vault.save()
    print(f"Set {args.key}")


def cmd_get(args):
    password = get_password(args)
    vault = Vault(args.vault, password)
    value = vault.get(args.key)
    if value is None:
        print(f"Key '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)
    print(value)


def cmd_list(args):
    password = get_password(args)
    vault = Vault(args.vault, password)
    keys = vault.list_keys()
    if not keys:
        print("(empty vault)")
    else:
        for key in sorted(keys):
            print(key)


def cmd_delete(args):
    password = get_password(args)
    vault = Vault(args.vault, password)
    vault.delete(args.key)
    vault.save()
    print(f"Deleted {args.key}")


def cmd_diff(args):
    password = get_password(args)
    vault_a = Vault(args.vault, password)
    vault_b = Vault(args.other, password)
    diff = generate_diff(vault_a.to_dict(), vault_b.to_dict())
    print(diff_summary(diff))
    if args.output:
        Path(args.output).write_text(serialize_diff(diff))
        print(f"Diff written to {args.output}")


def cmd_apply(args):
    password = get_password(args)
    vault = Vault(args.vault, password)
    diff = deserialize_diff(Path(args.diff_file).read_text())
    updated = apply_diff(vault.to_dict(), diff)
    vault.from_dict(updated)
    vault.save()
    print(f"Applied diff from {args.diff_file}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Encrypted local environment variable manager",
    )
    parser.add_argument("--vault", default=DEFAULT_VAULT_PATH, help="Path to vault directory")
    parser.add_argument("--password", default=None, help="Vault password (prefer env var)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="Set a key-value pair")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="Get a value by key")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list", help="List all keys")
    p_list.set_defaults(func=cmd_list)

    p_del = sub.add_parser("delete", help="Delete a key")
    p_del.add_argument("key")
    p_del.set_defaults(func=cmd_delete)

    p_diff = sub.add_parser("diff", help="Show diff between two vaults")
    p_diff.add_argument("other", help="Path to second vault")
    p_diff.add_argument("--output", default=None, help="Write diff to file")
    p_diff.set_defaults(func=cmd_diff)

    p_apply = sub.add_parser("apply", help="Apply a diff file to vault")
    p_apply.add_argument("diff_file", help="Path to diff file")
    p_apply.set_defaults(func=cmd_apply)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
