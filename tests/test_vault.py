"""Tests for the Vault class."""

import pytest
from pathlib import Path

from envault.vault import Vault

PASSWORD = "supersecret"


@pytest.fixture
def vault(tmp_path):
    return Vault(
        vault_path=str(tmp_path / ".envault"),
        salt_path=str(tmp_path / ".envault.salt"),
    )


class TestVaultSetGet:
    def test_set_and_get(self, vault):
        vault.set("API_KEY", "abc123")
        assert vault.get("API_KEY") == "abc123"

    def test_get_missing_key_returns_none(self, vault):
        assert vault.get("NONEXISTENT") is None

    def test_overwrite_existing_key(self, vault):
        vault.set("KEY", "old")
        vault.set("KEY", "new")
        assert vault.get("KEY") == "new"


class TestVaultDelete:
    def test_delete_existing_key(self, vault):
        vault.set("TO_DELETE", "value")
        result = vault.delete("TO_DELETE")
        assert result is True
        assert vault.get("TO_DELETE") is None

    def test_delete_nonexistent_key(self, vault):
        result = vault.delete("GHOST")
        assert result is False


class TestVaultListKeys:
    def test_list_keys_empty(self, vault):
        assert vault.list_keys() == []

    def test_list_keys_sorted(self, vault):
        vault.set("ZEBRA", "1")
        vault.set("ALPHA", "2")
        vault.set("MIDDLE", "3")
        assert vault.list_keys() == ["ALPHA", "MIDDLE", "ZEBRA"]


class TestVaultPersistence:
    def test_save_and_load(self, vault):
        vault.set("DB_URL", "postgres://localhost/mydb")
        vault.set("SECRET", "topsecret")
        vault.save(PASSWORD)

        vault2 = Vault(vault_path=str(vault.vault_path), salt_path=str(vault.salt_path))
        vault2.load(PASSWORD)

        assert vault2.get("DB_URL") == "postgres://localhost/mydb"
        assert vault2.get("SECRET") == "topsecret"

    def test_load_nonexistent_vault_is_empty(self, vault):
        vault.load(PASSWORD)
        assert vault.list_keys() == []

    def test_wrong_password_raises(self, vault):
        vault.set("KEY", "value")
        vault.save(PASSWORD)

        vault2 = Vault(vault_path=str(vault.vault_path), salt_path=str(vault.salt_path))
        with pytest.raises(Exception):
            vault2.load("wrongpassword")

    def test_export_returns_copy(self, vault):
        vault.set("A", "1")
        exported = vault.export()
        exported["B"] = "2"
        assert vault.get("B") is None
