"""Backup and restore support for envault vaults."""

import json
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def create_backup(vault_dir: str | Path, backup_path: str | Path | None = None) -> Path:
    """Create a compressed backup of the vault directory.

    Args:
        vault_dir: Path to the vault directory.
        backup_path: Optional explicit output path for the .tar.gz file.
                     Defaults to <vault_dir>/backups/<timestamp>.tar.gz.

    Returns:
        Path to the created backup file.
    """
    vault_dir = Path(vault_dir)
    if not vault_dir.exists():
        raise FileNotFoundError(f"Vault directory not found: {vault_dir}")

    if backup_path is None:
        backups_dir = vault_dir / "backups"
        backups_dir.mkdir(exist_ok=True)
        backup_path = backups_dir / f"{_timestamp()}.tar.gz"

    backup_path = Path(backup_path)
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(backup_path, "w:gz") as tar:
        for item in vault_dir.iterdir():
            if item.name == "backups":
                continue
            tar.add(item, arcname=item.name)

    return backup_path


def restore_backup(backup_path: str | Path, vault_dir: str | Path, overwrite: bool = False) -> list[str]:
    """Restore a vault from a backup archive.

    Args:
        backup_path: Path to the .tar.gz backup file.
        vault_dir: Destination vault directory.
        overwrite: If True, existing files will be replaced.

    Returns:
        List of restored file names.
    """
    backup_path = Path(backup_path)
    vault_dir = Path(vault_dir)

    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    vault_dir.mkdir(parents=True, exist_ok=True)
    restored: list[str] = []

    with tarfile.open(backup_path, "r:gz") as tar:
        for member in tar.getmembers():
            dest = vault_dir / member.name
            if dest.exists() and not overwrite:
                continue
            tar.extract(member, path=vault_dir)
            restored.append(member.name)

    return restored


def list_backups(vault_dir: str | Path) -> list[dict]:
    """List available backups for a vault.

    Returns a list of dicts with 'path', 'name', and 'size_bytes' keys.
    """
    backups_dir = Path(vault_dir) / "backups"
    if not backups_dir.exists():
        return []

    result = []
    for f in sorted(backups_dir.glob("*.tar.gz")):
        result.append({
            "path": str(f),
            "name": f.name,
            "size_bytes": f.stat().st_size,
        })
    return result
