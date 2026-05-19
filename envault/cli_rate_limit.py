"""CLI commands for rate limit management."""

import argparse

from envault.rate_limit import (
    check_rate_limit,
    get_rate_limit,
    list_rate_limits,
    remove_rate_limit,
    reset_calls,
    set_rate_limit,
)


def cmd_ratelimit_set(args: argparse.Namespace) -> None:
    entry = set_rate_limit(
        args.vault_dir, args.operation, args.max_calls, args.window
    )
    print(
        f"Rate limit set: '{args.operation}' — "
        f"{entry['max_calls']} calls per {entry['window_seconds']}s"
    )


def cmd_ratelimit_remove(args: argparse.Namespace) -> None:
    removed = remove_rate_limit(args.vault_dir, args.operation)
    if removed:
        print(f"Rate limit removed for '{args.operation}'.")
    else:
        print(f"No rate limit found for '{args.operation}'.")


def cmd_ratelimit_check(args: argparse.Namespace) -> None:
    allowed, retry_after = check_rate_limit(args.vault_dir, args.operation)
    if allowed:
        print(f"Allowed: '{args.operation}' is within rate limit.")
    else:
        print(
            f"Denied: '{args.operation}' exceeded rate limit. "
            f"Retry after {retry_after}s."
        )


def cmd_ratelimit_show(args: argparse.Namespace) -> None:
    entry = get_rate_limit(args.vault_dir, args.operation)
    if entry is None:
        print(f"No rate limit configured for '{args.operation}'.")
        return
    calls = len([c for c in entry["calls"]])
    print(
        f"Operation : {args.operation}\n"
        f"Max calls : {entry['max_calls']}\n"
        f"Window    : {entry['window_seconds']}s\n"
        f"Current   : {calls} call(s) recorded"
    )


def cmd_ratelimit_list(args: argparse.Namespace) -> None:
    limits = list_rate_limits(args.vault_dir)
    if not limits:
        print("No rate limits configured.")
        return
    for op, entry in sorted(limits.items()):
        print(f"  {op}: {entry['max_calls']} calls / {entry['window_seconds']}s")


def cmd_ratelimit_reset(args: argparse.Namespace) -> None:
    ok = reset_calls(args.vault_dir, args.operation)
    if ok:
        print(f"Call history reset for '{args.operation}'.")
    else:
        print(f"No rate limit found for '{args.operation}'.")


def register_ratelimit_commands(subparsers, parent_kwargs: dict) -> None:
    p = subparsers.add_parser("ratelimit", help="Manage operation rate limits")
    sub = p.add_subparsers(dest="ratelimit_cmd", required=True)

    s = sub.add_parser("set", **parent_kwargs)
    s.add_argument("operation")
    s.add_argument("max_calls", type=int)
    s.add_argument("window", type=int, help="Window in seconds")
    s.set_defaults(func=cmd_ratelimit_set)

    r = sub.add_parser("remove", **parent_kwargs)
    r.add_argument("operation")
    r.set_defaults(func=cmd_ratelimit_remove)

    c = sub.add_parser("check", **parent_kwargs)
    c.add_argument("operation")
    c.set_defaults(func=cmd_ratelimit_check)

    sh = sub.add_parser("show", **parent_kwargs)
    sh.add_argument("operation")
    sh.set_defaults(func=cmd_ratelimit_show)

    ls = sub.add_parser("list", **parent_kwargs)
    ls.set_defaults(func=cmd_ratelimit_list)

    rs = sub.add_parser("reset", **parent_kwargs)
    rs.add_argument("operation")
    rs.set_defaults(func=cmd_ratelimit_reset)
