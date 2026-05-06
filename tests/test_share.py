"""Tests for envault.share module."""

import json
import os
import pytest

from envault.vault import Vault
from envault.share import export_share_patch, import_share_patch


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def source_vault(vault_dir):
    v = Vault(os.path.join(vault_dir, "source"), "source-pass")
    v.set("API_KEY", "abc123")
    v.set("DB_URL", "postgres://localhost/db")
    v.set("SECRET", "topsecret")
    return v


@pytest.fixture
def target_vault(vault_dir):
    v = Vault(os.path.join(vault_dir, "target"), "target-pass")
    return v


class TestExportSharePatch:
    def test_creates_patch_file(self, source_vault, vault_dir):
        patch_path = export_share_patch(source_vault, "recipient-pass")
        assert os.path.exists(patch_path)

    def test_patch_is_valid_json(self, source_vault):
        patch_path = export_share_patch(source_vault, "recipient-pass")
        with open(patch_path) as f:
            data = json.load(f)
        assert "diff" in data
        assert "salt" in data

    def test_patch_with_base_vault(self, vault_dir):
        base = Vault(os.path.join(vault_dir, "base"), "pass")
        base.set("API_KEY", "old")

        current = Vault(os.path.join(vault_dir, "current"), "pass")
        current.set("API_KEY", "new")
        current.set("NEW_KEY", "value")

        patch_path = export_share_patch(current, "recipient-pass", base_vault=base)
        assert os.path.exists(patch_path)


class TestImportSharePatch:
    def test_imports_all_keys(self, source_vault, target_vault):
        patch_path = export_share_patch(source_vault, "shared-pass")
        result = import_share_patch(patch_path, "shared-pass", target_vault)
        assert set(result["added"]) == {"API_KEY", "DB_URL", "SECRET"}

    def test_values_match_after_import(self, source_vault, target_vault):
        patch_path = export_share_patch(source_vault, "shared-pass")
        import_share_patch(patch_path, "shared-pass", target_vault)
        assert target_vault.get("API_KEY") == "abc123"
        assert target_vault.get("DB_URL") == "postgres://localhost/db"

    def test_modified_keys_detected(self, vault_dir):
        base = Vault(os.path.join(vault_dir, "base2"), "pass")
        base.set("KEY", "old_value")

        updated = Vault(os.path.join(vault_dir, "updated"), "pass")
        updated.set("KEY", "new_value")

        target = Vault(os.path.join(vault_dir, "target2"), "pass")
        target.set("KEY", "old_value")

        patch_path = export_share_patch(updated, "shared-pass", base_vault=base)
        result = import_share_patch(patch_path, "shared-pass", target)
        assert "KEY" in result["modified"]

    def test_removed_keys_applied(self, vault_dir):
        base = Vault(os.path.join(vault_dir, "base3"), "pass")
        base.set("OLD_KEY", "value")
        base.set("KEEP_KEY", "keep")

        current = Vault(os.path.join(vault_dir, "current3"), "pass")
        current.set("KEEP_KEY", "keep")

        target = Vault(os.path.join(vault_dir, "target3"), "pass")
        target.set("OLD_KEY", "value")
        target.set("KEEP_KEY", "keep")

        patch_path = export_share_patch(current, "shared-pass", base_vault=base)
        result = import_share_patch(patch_path, "shared-pass", target)
        assert "OLD_KEY" in result["removed"]
        assert target_vault_has_key(target, "OLD_KEY") is False


def target_vault_has_key(vault, key):
    return key in vault.list_keys()
