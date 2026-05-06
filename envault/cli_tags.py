"""CLI commands for tag management."""

from __future__ import annotations

import argparse

from envault import tags as tag_mod


def cmd_tag_add(args: argparse.Namespace) -> None:
    """envault tag add <key> <tag>"""
    tag_mod.add_tag(args.vault_dir, args.key, args.tag)
    print(f"Tag '{args.tag}' added to '{args.key}'.")


def cmd_tag_remove(args: argparse.Namespace) -> None:
    """envault tag remove <key> <tag>"""
    removed = tag_mod.remove_tag(args.vault_dir, args.key, args.tag)
    if removed:
        print(f"Tag '{args.tag}' removed from '{args.key}'.")
    else:
        print(f"Tag '{args.tag}' not found on '{args.key}'.")


def cmd_tag_list(args: argparse.Namespace) -> None:
    """envault tag list [--tag TAG]"""
    if args.tag:
        keys = tag_mod.keys_for_tag(args.vault_dir, args.tag)
        if keys:
            print(f"Keys tagged '{args.tag}':")
            for k in keys:
                print(f"  {k}")
        else:
            print(f"No keys found with tag '{args.tag}'.")
    else:
        summary = tag_mod.tags_summary(args.vault_dir)
        print(summary)


def cmd_tag_all(args: argparse.Namespace) -> None:
    """envault tag all — list every distinct tag."""
    all_t = tag_mod.all_tags(args.vault_dir)
    if all_t:
        print("All tags: " + ", ".join(all_t))
    else:
        print("No tags defined.")


def register_tag_commands(subparsers: argparse._SubParsersAction, vault_dir: str) -> None:
    tag_parser = subparsers.add_parser("tag", help="Manage key tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd")

    p_add = tag_sub.add_parser("add", help="Add a tag to a key")
    p_add.add_argument("key")
    p_add.add_argument("tag")
    p_add.set_defaults(func=cmd_tag_add, vault_dir=vault_dir)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a key")
    p_rm.add_argument("key")
    p_rm.add_argument("tag")
    p_rm.set_defaults(func=cmd_tag_remove, vault_dir=vault_dir)

    p_ls = tag_sub.add_parser("list", help="List tags or keys for a tag")
    p_ls.add_argument("--tag", default=None, help="Filter keys by this tag")
    p_ls.set_defaults(func=cmd_tag_list, vault_dir=vault_dir)

    p_all = tag_sub.add_parser("all", help="Show all distinct tags")
    p_all.set_defaults(func=cmd_tag_all, vault_dir=vault_dir)
