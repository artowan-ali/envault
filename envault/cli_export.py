"""CLI commands for export/import of vault secrets."""

import sys
from typing import Optional

from envault.export import (
    detect_format,
    export_to_env,
    export_to_json,
    import_from_env,
    import_from_json,
)
from envault.vault import Vault


def cmd_export(args, vault: Optional[Vault] = None) -> None:
    """Export vault secrets to a file."""
    if vault is None:
        from envault.cli import get_password
        password = get_password(confirm=False)
        vault = Vault(args.vault_dir, password)

    fmt = args.format if hasattr(args, "format") and args.format else detect_format(args.output)
    if fmt is None:
        fmt = "env"

    secrets = {key: vault.get(key) for key in vault.list()}

    if fmt == "json":
        export_to_json(secrets, args.output)
    else:
        export_to_env(secrets, args.output)

    print(f"Exported {len(secrets)} secret(s) to {args.output} ({fmt} format)")


def cmd_import(args, vault: Optional[Vault] = None) -> None:
    """Import secrets from a file into the vault."""
    if vault is None:
        from envault.cli import get_password
        password = get_password(confirm=False)
        vault = Vault(args.vault_dir, password)

    fmt = args.format if hasattr(args, "format") and args.format else detect_format(args.input)
    if fmt is None:
        fmt = "env"

    try:
        if fmt == "json":
            secrets = import_from_json(args.input)
        else:
            secrets = import_from_env(args.input)
    except (OSError, ValueError) as exc:
        print(f"Error reading {args.input}: {exc}", file=sys.stderr)
        sys.exit(1)

    overwritten = 0
    for key, value in secrets.items():
        if vault.get(key) is not None:
            overwritten += 1
        vault.set(key, value)

    new_count = len(secrets) - overwritten
    print(
        f"Imported {len(secrets)} secret(s) from {args.input} "
        f"({new_count} new, {overwritten} overwritten)"
    )
