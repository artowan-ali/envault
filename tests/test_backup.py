"""Tests for envault.backup module."""

import tarfile
from pathlib import Path

import pytest

from envault.backup import create_backup, list_backups, restore_backup


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    vd = tmp_path / "vault"
    vd.mkdir()
    (vd / "store.enc").write_bytes(b"encrypted-data")
    (vd / "salt.bin").write_bytes(b"saltsalt")
    (vd / "audit.json").write_text('[{"event": "set"}]')
    return vd


class TestCreateBackup:
    def test_creates_tar_gz_file(self, vault_dir: Path) -> None:
        backup = create_backup(vault_dir)
        assert backup.exists()
        assert backup.suffix == ".gz"
        assert ".tar" in backup.name

    def test_backup_placed_in_backups_subdir_by_default(self, vault_dir: Path) -> None:
        backup = create_backup(vault_dir)
        assert backup.parent == vault_dir / "backups"

    def test_custom_backup_path(self, vault_dir: Path, tmp_path: Path) -> None:
        custom = tmp_path / "my_backup.tar.gz"
        result = create_backup(vault_dir, backup_path=custom)
        assert result == custom
        assert custom.exists()

    def test_archive_contains_vault_files(self, vault_dir: Path) -> None:
        backup = create_backup(vault_dir)
        with tarfile.open(backup, "r:gz") as tar:
            names = tar.getnames()
        assert "store.enc" in names
        assert "salt.bin" in names

    def test_backups_subdir_not_included_in_archive(self, vault_dir: Path) -> None:
        backup = create_backup(vault_dir)
        with tarfile.open(backup, "r:gz") as tar:
            names = tar.getnames()
        assert not any(n.startswith("backups") for n in names)

    def test_raises_if_vault_dir_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            create_backup(tmp_path / "nonexistent")


class TestRestoreBackup:
    def test_restores_files_to_destination(self, vault_dir: Path, tmp_path: Path) -> None:
        backup = create_backup(vault_dir)
        dest = tmp_path / "restored"
        restored = restore_backup(backup, dest)
        assert (dest / "store.enc").exists()
        assert "store.enc" in restored

    def test_returns_list_of_restored_names(self, vault_dir: Path, tmp_path: Path) -> None:
        backup = create_backup(vault_dir)
        dest = tmp_path / "restored"
        restored = restore_backup(backup, dest)
        assert isinstance(restored, list)
        assert len(restored) > 0

    def test_does_not_overwrite_by_default(self, vault_dir: Path, tmp_path: Path) -> None:
        backup = create_backup(vault_dir)
        dest = tmp_path / "restored"
        dest.mkdir()
        original_content = b"do-not-touch"
        (dest / "store.enc").write_bytes(original_content)
        restore_backup(backup, dest, overwrite=False)
        assert (dest / "store.enc").read_bytes() == original_content

    def test_overwrite_replaces_existing_files(self, vault_dir: Path, tmp_path: Path) -> None:
        backup = create_backup(vault_dir)
        dest = tmp_path / "restored"
        dest.mkdir()
        (dest / "store.enc").write_bytes(b"old-data")
        restore_backup(backup, dest, overwrite=True)
        assert (dest / "store.enc").read_bytes() == b"encrypted-data"

    def test_raises_if_backup_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            restore_backup(tmp_path / "no.tar.gz", tmp_path / "dest")


class TestListBackups:
    def test_returns_empty_when_no_backups(self, vault_dir: Path) -> None:
        assert list_backups(vault_dir) == []

    def test_lists_created_backups(self, vault_dir: Path) -> None:
        create_backup(vault_dir)
        backups = list_backups(vault_dir)
        assert len(backups) == 1
        assert "name" in backups[0]
        assert "path" in backups[0]
        assert "size_bytes" in backups[0]

    def test_size_bytes_is_positive(self, vault_dir: Path) -> None:
        create_backup(vault_dir)
        backups = list_backups(vault_dir)
        assert backups[0]["size_bytes"] > 0
