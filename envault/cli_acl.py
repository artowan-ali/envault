"""CLI commands for ACL (access control list) management."""

import sys
from envault.acl import (
    set_permission,
    remove_permission,
    get_permissions,
    list_acl,
    list_all_acl,
    VALID_PERMISSIONS,
)


def cmd_acl_set(args):
    """Grant permissions to a user on a key."""
    permissions = [p.strip() for p in args.permissions.split(",")]
    try:
        set_permission(args.vault_dir, args.key, args.user, permissions)
        print(f"Granted {permissions} on '{args.key}' to '{args.user}'.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_acl_remove(args):
    """Remove a user's permissions on a key."""
    removed = remove_permission(args.vault_dir, args.key, args.user)
    if removed:
        print(f"Removed permissions for '{args.user}' on '{args.key}'.")
    else:
        print(f"No permissions found for '{args.user}' on '{args.key}'.")


def cmd_acl_check(args):
    """Check if a user has a specific permission on a key."""
    perms = get_permissions(args.vault_dir, args.key, args.user)
    if args.permission in perms:
        print(f"'{args.user}' has '{args.permission}' on '{args.key}'.")
    else:
        print(f"'{args.user}' does NOT have '{args.permission}' on '{args.key}'.")
        sys.exit(1)


def cmd_acl_list(args):
    """List all permissions for a key."""
    mapping = list_acl(args.vault_dir, args.key)
    if not mapping:
        print(f"No ACL entries for '{args.key}'.")
        return
    for user, perms in sorted(mapping.items()):
        print(f"  {user}: {', '.join(perms)}")


def cmd_acl_all(args):
    """List the full ACL for the vault."""
    acl = list_all_acl(args.vault_dir)
    if not acl:
        print("No ACL entries found.")
        return
    for key, users in sorted(acl.items()):
        print(f"{key}:")
        for user, perms in sorted(users.items()):
            print(f"  {user}: {', '.join(perms)}")


def register_acl_commands(subparsers, vault_dir):
    acl_parser = subparsers.add_parser("acl", help="Manage key access control lists")
    acl_sub = acl_parser.add_subparsers(dest="acl_cmd")

    p_set = acl_sub.add_parser("set", help="Grant permissions to a user")
    p_set.add_argument("key")
    p_set.add_argument("user")
    p_set.add_argument("permissions", help="Comma-separated: read,write,delete")
    p_set.set_defaults(func=cmd_acl_set, vault_dir=vault_dir)

    p_rm = acl_sub.add_parser("remove", help="Remove user permissions on a key")
    p_rm.add_argument("key")
    p_rm.add_argument("user")
    p_rm.set_defaults(func=cmd_acl_remove, vault_dir=vault_dir)

    p_chk = acl_sub.add_parser("check", help="Check if user has a permission")
    p_chk.add_argument("key")
    p_chk.add_argument("user")
    p_chk.add_argument("permission", choices=list(VALID_PERMISSIONS))
    p_chk.set_defaults(func=cmd_acl_check, vault_dir=vault_dir)

    p_ls = acl_sub.add_parser("list", help="List ACL for a key")
    p_ls.add_argument("key")
    p_ls.set_defaults(func=cmd_acl_list, vault_dir=vault_dir)

    p_all = acl_sub.add_parser("all", help="List full vault ACL")
    p_all.set_defaults(func=cmd_acl_all, vault_dir=vault_dir)
