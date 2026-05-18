"""CLI commands for session management."""

import argparse

from envault.session import (
    clear_session,
    save_session,
    session_status,
    DEFAULT_SESSION_TTL,
)


def cmd_session_start(args: argparse.Namespace) -> None:
    """Cache the vault password for a limited time."""
    import getpass

    password = getpass.getpass("Vault password: ")
    ttl = getattr(args, "ttl", DEFAULT_SESSION_TTL)
    save_session(args.vault_dir, password, ttl=ttl)
    print(f"Session started. Password cached for {ttl} seconds.")


def cmd_session_status(args: argparse.Namespace) -> None:
    """Show whether a session is currently active."""
    status = session_status(args.vault_dir)
    if status["active"]:
        print(
            f"Session active. Expires in {status['remaining_seconds']}s "
            f"(at {status['expires_at']:.0f})."
        )
    else:
        print("No active session.")


def cmd_session_end(args: argparse.Namespace) -> None:
    """Clear the cached session password."""
    clear_session(args.vault_dir)
    print("Session cleared.")


def register_session_commands(subparsers, parent_parser) -> None:
    session_parser = subparsers.add_parser("session", help="Manage unlock sessions")
    session_sub = session_parser.add_subparsers(dest="session_cmd")

    start_p = session_sub.add_parser("start", parents=[parent_parser], help="Start a session")
    start_p.add_argument(
        "--ttl",
        type=int,
        default=DEFAULT_SESSION_TTL,
        help="Session lifetime in seconds (default: 900)",
    )
    start_p.set_defaults(func=cmd_session_start)

    status_p = session_sub.add_parser("status", parents=[parent_parser], help="Show session status")
    status_p.set_defaults(func=cmd_session_status)

    end_p = session_sub.add_parser("end", parents=[parent_parser], help="End the current session")
    end_p.set_defaults(func=cmd_session_end)
