"""CLI commands for alias management."""

import argparse
from envault.alias import set_alias, remove_alias, resolve_alias, list_aliases, rename_alias


def cmd_alias_set(args: argparse.Namespace) -> None:
    set_alias(args.vault_dir, args.alias, args.key)
    print(f"Alias '{args.alias}' -> '{args.key}' set.")


def cmd_alias_remove(args: argparse.Namespace) -> None:
    removed = remove_alias(args.vault_dir, args.alias)
    if removed:
        print(f"Alias '{args.alias}' removed.")
    else:
        print(f"Alias '{args.alias}' not found.")


def cmd_alias_resolve(args: argparse.Namespace) -> None:
    key = resolve_alias(args.vault_dir, args.alias)
    if key is not None:
        print(key)
    else:
        print(f"No alias named '{args.alias}'.")


def cmd_alias_list(args: argparse.Namespace) -> None:
    aliases = list_aliases(args.vault_dir)
    if not aliases:
        print("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        print(f"  {alias} -> {key}")


def cmd_alias_rename(args: argparse.Namespace) -> None:
    success = rename_alias(args.vault_dir, args.old_alias, args.new_alias)
    if success:
        print(f"Alias '{args.old_alias}' renamed to '{args.new_alias}'.")
    else:
        print(f"Alias '{args.old_alias}' not found.")


def register_alias_commands(subparsers, parent_kwargs: dict) -> None:
    alias_p = subparsers.add_parser("alias", help="Manage key aliases")
    alias_sub = alias_p.add_subparsers(dest="alias_cmd")

    p_set = alias_sub.add_parser("set", **parent_kwargs)
    p_set.add_argument("alias", help="Alias name")
    p_set.add_argument("key", help="Vault key to point to")
    p_set.set_defaults(func=cmd_alias_set)

    p_rm = alias_sub.add_parser("remove", **parent_kwargs)
    p_rm.add_argument("alias", help="Alias name")
    p_rm.set_defaults(func=cmd_alias_remove)

    p_res = alias_sub.add_parser("resolve", **parent_kwargs)
    p_res.add_argument("alias", help="Alias name")
    p_res.set_defaults(func=cmd_alias_resolve)

    p_ls = alias_sub.add_parser("list", **parent_kwargs)
    p_ls.set_defaults(func=cmd_alias_list)

    p_rn = alias_sub.add_parser("rename", **parent_kwargs)
    p_rn.add_argument("old_alias", help="Current alias name")
    p_rn.add_argument("new_alias", help="New alias name")
    p_rn.set_defaults(func=cmd_alias_rename)
