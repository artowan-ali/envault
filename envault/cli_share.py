"""CLI commands for team sharing via encrypted patches."""

import argparse
import os
import sys

from envault.cli import get_password
from envault.vault import Vault
from envault.share import export_share_patch, import_share_patch


def cmd_share_export(args):
    """Export an encrypted share patch for a recipient."""
    password = get_password("Vault password: ")
    vault = Vault(args.vault_dir, password)

    base_vault = None
    if args.base_dir:
        base_password = get_password("Base vault password (or same): ")
        base_vault = Vault(args.base_dir, base_password)

    recipient_password = get_password("Recipient password: ")
    confirm = get_password("Confirm recipient password: ")
    if recipient_password != confirm:
        print("Error: passwords do not match.", file=sys.stderr)
        sys.exit(1)

    patch_path = export_share_patch(vault, recipient_password, base_vault=base_vault)
    print(f"Share patch written to: {patch_path}")
    print("Share this file and the recipient password with your team member.")


def cmd_share_import(args):
    """Import an encrypted share patch into the local vault."""
    if not os.path.exists(args.patch_file):
        print(f"Error: patch file not found: {args.patch_file}", file=sys.stderr)
        sys.exit(1)

    recipient_password = get_password("Recipient password (from sender): ")
    vault_password = get_password("Local vault password: ")
    vault = Vault(args.vault_dir, vault_password)

    result = import_share_patch(args.patch_file, recipient_password, vault)

    added = result["added"]
    modified = result["modified"]
    removed = result["removed"]

    if added:
        print(f"Added ({len(added)}): {', '.join(sorted(added))}")
    if modified:
        print(f"Modified ({len(modified)}): {', '.join(sorted(modified))}")
    if removed:
        print(f"Removed ({len(removed)}): {', '.join(sorted(removed))}")
    if not any([added, modified, removed]):
        print("No changes applied.")
    else:
        total = len(added) + len(modified) + len(removed)
        print(f"Done. {total} key(s) updated.")


def register_share_commands(subparsers):
    """Register share subcommands onto an argparse subparsers object."""
    p_export = subparsers.add_parser("share-export", help="Export encrypted share patch")
    p_export.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p_export.add_argument("--base-dir", default=None, help="Base vault dir for diff-only export")
    p_export.set_defaults(func=cmd_share_export)

    p_import = subparsers.add_parser("share-import", help="Import encrypted share patch")
    p_import.add_argument("patch_file", help="Path to the .patch file")
    p_import.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p_import.set_defaults(func=cmd_share_import)
