"""CLI commands for profile management."""

import argparse
from envault.profile import (
    set_profile_key,
    get_profile_key,
    delete_profile_key,
    list_profiles,
    get_profile,
    delete_profile,
    profile_summary,
)


def cmd_profile_set(args: argparse.Namespace) -> None:
    set_profile_key(args.vault_dir, args.profile, args.key, args.value)
    print(f"Set '{args.key}' in profile '{args.profile}'.")


def cmd_profile_get(args: argparse.Namespace) -> None:
    value = get_profile_key(args.vault_dir, args.profile, args.key)
    if value is None:
        print(f"Key '{args.key}' not found in profile '{args.profile}'.")
    else:
        print(value)


def cmd_profile_delete_key(args: argparse.Namespace) -> None:
    removed = delete_profile_key(args.vault_dir, args.profile, args.key)
    if removed:
        print(f"Removed '{args.key}' from profile '{args.profile}'.")
    else:
        print(f"Key '{args.key}' not found in profile '{args.profile}'.")


def cmd_profile_list(args: argparse.Namespace) -> None:
    profiles = list_profiles(args.vault_dir)
    if not profiles:
        print("No profiles defined.")
    else:
        for name in profiles:
            print(name)


def cmd_profile_show(args: argparse.Namespace) -> None:
    data = get_profile(args.vault_dir, args.profile)
    if not data:
        print(f"Profile '{args.profile}' is empty or does not exist.")
    else:
        for key, value in sorted(data.items()):
            print(f"{key}={value}")


def cmd_profile_delete(args: argparse.Namespace) -> None:
    removed = delete_profile(args.vault_dir, args.profile)
    if removed:
        print(f"Deleted profile '{args.profile}'.")
    else:
        print(f"Profile '{args.profile}' does not exist.")


def cmd_profile_summary(args: argparse.Namespace) -> None:
    print(profile_summary(args.vault_dir))


def register_profile_commands(subparsers, parent_kwargs: dict) -> None:
    p = subparsers.add_parser("profile", help="Manage named profiles")
    sub = p.add_subparsers(dest="profile_cmd")

    ps = sub.add_parser("set", **parent_kwargs)
    ps.add_argument("profile"); ps.add_argument("key"); ps.add_argument("value")
    ps.set_defaults(func=cmd_profile_set)

    pg = sub.add_parser("get", **parent_kwargs)
    pg.add_argument("profile"); pg.add_argument("key")
    pg.set_defaults(func=cmd_profile_get)

    pdk = sub.add_parser("delete-key", **parent_kwargs)
    pdk.add_argument("profile"); pdk.add_argument("key")
    pdk.set_defaults(func=cmd_profile_delete_key)

    pl = sub.add_parser("list", **parent_kwargs)
    pl.set_defaults(func=cmd_profile_list)

    psh = sub.add_parser("show", **parent_kwargs)
    psh.add_argument("profile")
    psh.set_defaults(func=cmd_profile_show)

    pd = sub.add_parser("delete", **parent_kwargs)
    pd.add_argument("profile")
    pd.set_defaults(func=cmd_profile_delete)

    psum = sub.add_parser("summary", **parent_kwargs)
    psum.set_defaults(func=cmd_profile_summary)
