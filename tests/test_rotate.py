"""Tests for envault.rotate key-rotation functionality."""

import pytest
from pathlib import Path
from envault.vault import Vault
from envault.rotate import rotate_key


@pytest.fixture
def vault_dir(tmp_path):
    """Return a temporary vault directory pre-populated with test secrets."""
    v = Vault(str(tmp_path), "old-password")
    v.set("DB_HOST", "localhost")
    v.set("DB_PORT", "5432")
    v.set("API_KEY", "supersecret")
    return tmp_path


class TestRotateKey:
    def test_returns_correct_count(self, vault_dir):
        result = rotate_key(str(vault_dir), "old-password", "new-password")
        assert result["rotated"] == 3

    def test_returns_key_names(self, vault_dir):
        result = rotate_key(str(vault_dir), "old-password", "new-password")
        assert set(result["keys"]) == {"DB_HOST", "DB_PORT", "API_KEY"}

    def test_new_password_decrypts_values(self, vault_dir):
        rotate_key(str(vault_dir), "old-password", "new-password")
        new_vault = Vault(str(vault_dir), "new-password")
        assert new_vault.get("DB_HOST") == "localhost"
        assert new_vault.get("DB_PORT") == "5432"
        assert new_vault.get("API_KEY") == "supersecret"

    def test_old_password_cannot_decrypt_after_rotation(self, vault_dir):
        rotate_key(str(vault_dir), "old-password", "new-password")
        old_vault = Vault(str(vault_dir), "old-password")
        # Values should not be recoverable with the old password
        for key in ["DB_HOST", "DB_PORT", "API_KEY"]:
            value = old_vault.get(key)
            assert value != "localhost" or key != "DB_HOST"

    def test_salt_file_regenerated(self, vault_dir):
        old_salt = (vault_dir / "salt").read_bytes()
        rotate_key(str(vault_dir), "old-password", "new-password")
        new_salt = (vault_dir / "salt").read_bytes()
        assert old_salt != new_salt

    def test_raises_if_vault_dir_missing(self, tmp_path):
        missing = str(tmp_path / "nonexistent")
        with pytest.raises(FileNotFoundError):
            rotate_key(missing, "old", "new")

    def test_audit_event_recorded(self, vault_dir):
        from envault.audit import get_log
        rotate_key(str(vault_dir), "old-password", "new-password")
        log = get_log(str(vault_dir))
        events = [e["event"] for e in log]
        assert "rotate_key" in events

    def test_empty_vault_rotation(self, tmp_path):
        Vault(str(tmp_path), "old-password")  # create empty vault
        result = rotate_key(str(tmp_path), "old-password", "new-password")
        assert result["rotated"] == 0
        assert result["keys"] == []
