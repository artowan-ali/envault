"""CLI commands for PIN-based quick unlock."""

import argparse

from envault.pin import set_pin, verify_pin, remove_pin, pin_status


def cmd_pin_set(args: argparse.Namespace) -> None:
    """Set a PIN for the vault."""
    pin = args.pin
    if len(pin) < 4:
        print("Error: PIN must be at least 4 characters.")
        return
    set_pin(args.vault_dir, pin)
    print("PIN set successfully.")


def cmd_pin_verify(args: argparse.Namespace) -> None:
    """Verify a PIN against the stored hash."""
    if verify_pin(args.vault_dir, args.pin):
        print("PIN verified.")
    else:
        status = pin_status(args.vault_dir)
        if not status["set"]:
            print("No PIN is set for this vault.")
        elif status.get("expired"):
            print("PIN has expired. Please set a new PIN.")
        else:
            print("Invalid PIN.")


def cmd_pin_remove(args: argparse.Namespace) -> None:
    """Remove the stored PIN."""
    removed = remove_pin(args.vault_dir)
    if removed:
        print("PIN removed.")
    else:
        print("No PIN was set.")


def cmd_pin_status(args: argparse.Namespace) -> None:
    """Show current PIN status."""
    status = pin_status(args.vault_dir)
    if not status["set"]:
        print("PIN: not set")
        return
    expired = status.get("expired", False)
    age = status.get("age_seconds", 0)
    ttl = status.get("ttl_seconds", 0)
    remaining = max(0, ttl - age)
    print(f"PIN: set")
    print(f"  Expired : {expired}")
    print(f"  Age     : {age}s")
    print(f"  Expires in: {remaining}s")


def register_pin_commands(subparsers, parent_kwargs: dict) -> None:
    pin_p = subparsers.add_parser("pin", help="Manage quick-unlock PIN")
    pin_sub = pin_p.add_subparsers(dest="pin_cmd")

    p_set = pin_sub.add_parser("set", **parent_kwargs)
    p_set.add_argument("pin", help="PIN to set")
    p_set.set_defaults(func=cmd_pin_set)

    p_verify = pin_sub.add_parser("verify", **parent_kwargs)
    p_verify.add_argument("pin", help="PIN to verify")
    p_verify.set_defaults(func=cmd_pin_verify)

    p_remove = pin_sub.add_parser("remove", **parent_kwargs)
    p_remove.set_defaults(func=cmd_pin_remove)

    p_status = pin_sub.add_parser("status", **parent_kwargs)
    p_status.set_defaults(func=cmd_pin_status)
