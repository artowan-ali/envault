"""Tests for envault.alias module."""

import pytest
from pathlib import Path
from envault.alias import set_alias, remove_alias, resolve_alias, list_aliases, rename_alias


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndResolveAlias:
    def test_set_and_resolve(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        assert resolve_alias(vault_dir, "db") == "DATABASE_URL"

    def test_resolve_missing_returns_none(self, vault_dir):
        assert resolve_alias(vault_dir, "nonexistent") is None

    def test_overwrite_existing_alias(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        set_alias(vault_dir, "db", "DB_CONN_STRING")
        assert resolve_alias(vault_dir, "db") == "DB_CONN_STRING"

    def test_multiple_aliases(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        set_alias(vault_dir, "cache", "REDIS_URL")
        assert resolve_alias(vault_dir, "db") == "DATABASE_URL"
        assert resolve_alias(vault_dir, "cache") == "REDIS_URL"


class TestRemoveAlias:
    def test_remove_existing(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        result = remove_alias(vault_dir, "db")
        assert result is True
        assert resolve_alias(vault_dir, "db") is None

    def test_remove_nonexistent_returns_false(self, vault_dir):
        result = remove_alias(vault_dir, "ghost")
        assert result is False

    def test_remove_does_not_affect_others(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        set_alias(vault_dir, "cache", "REDIS_URL")
        remove_alias(vault_dir, "db")
        assert resolve_alias(vault_dir, "cache") == "REDIS_URL"


class TestListAliases:
    def test_empty_returns_empty_dict(self, vault_dir):
        assert list_aliases(vault_dir) == {}

    def test_lists_all_aliases(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        set_alias(vault_dir, "cache", "REDIS_URL")
        aliases = list_aliases(vault_dir)
        assert aliases == {"db": "DATABASE_URL", "cache": "REDIS_URL"}


class TestRenameAlias:
    def test_rename_existing(self, vault_dir):
        set_alias(vault_dir, "db", "DATABASE_URL")
        result = rename_alias(vault_dir, "db", "database")
        assert result is True
        assert resolve_alias(vault_dir, "database") == "DATABASE_URL"
        assert resolve_alias(vault_dir, "db") is None

    def test_rename_nonexistent_returns_false(self, vault_dir):
        result = rename_alias(vault_dir, "ghost", "phantom")
        assert result is False

    def test_aliases_file_created(self, vault_dir):
        set_alias(vault_dir, "x", "X_VAR")
        assert (Path(vault_dir) / "aliases.json").exists()
