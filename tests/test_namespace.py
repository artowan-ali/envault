"""Tests for envault.namespace module."""

import pytest
from pathlib import Path
from envault.namespace import (
    set_namespace,
    remove_namespace,
    get_namespace,
    list_namespace_keys,
    list_namespaces,
    namespace_summary,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndGetNamespace:
    def test_set_and_get(self, vault_dir):
        set_namespace(vault_dir, "DB_HOST", "database")
        assert get_namespace(vault_dir, "DB_HOST") == "database"

    def test_missing_key_returns_none(self, vault_dir):
        assert get_namespace(vault_dir, "MISSING") is None

    def test_overwrite_existing_namespace(self, vault_dir):
        set_namespace(vault_dir, "API_KEY", "api")
        set_namespace(vault_dir, "API_KEY", "secrets")
        assert get_namespace(vault_dir, "API_KEY") == "secrets"

    def test_multiple_keys_same_namespace(self, vault_dir):
        set_namespace(vault_dir, "DB_HOST", "database")
        set_namespace(vault_dir, "DB_PORT", "database")
        keys = list_namespace_keys(vault_dir, "database")
        assert keys == ["DB_HOST", "DB_PORT"]


class TestRemoveNamespace:
    def test_remove_existing_returns_true(self, vault_dir):
        set_namespace(vault_dir, "TOKEN", "auth")
        assert remove_namespace(vault_dir, "TOKEN") is True
        assert get_namespace(vault_dir, "TOKEN") is None

    def test_remove_missing_returns_false(self, vault_dir):
        assert remove_namespace(vault_dir, "NONEXISTENT") is False


class TestListNamespaces:
    def test_returns_unique_sorted_namespaces(self, vault_dir):
        set_namespace(vault_dir, "A", "zebra")
        set_namespace(vault_dir, "B", "alpha")
        set_namespace(vault_dir, "C", "alpha")
        assert list_namespaces(vault_dir) == ["alpha", "zebra"]

    def test_empty_vault_returns_empty(self, vault_dir):
        assert list_namespaces(vault_dir) == []


class TestListNamespaceKeys:
    def test_returns_sorted_keys(self, vault_dir):
        set_namespace(vault_dir, "Z_KEY", "group")
        set_namespace(vault_dir, "A_KEY", "group")
        set_namespace(vault_dir, "M_KEY", "other")
        assert list_namespace_keys(vault_dir, "group") == ["A_KEY", "Z_KEY"]

    def test_unknown_namespace_returns_empty(self, vault_dir):
        assert list_namespace_keys(vault_dir, "ghost") == []


class TestNamespaceSummary:
    def test_summary_groups_by_namespace(self, vault_dir):
        set_namespace(vault_dir, "DB_HOST", "db")
        set_namespace(vault_dir, "DB_PASS", "db")
        set_namespace(vault_dir, "API_KEY", "api")
        summary = namespace_summary(vault_dir)
        assert summary == {
            "db": ["DB_HOST", "DB_PASS"],
            "api": ["API_KEY"],
        }

    def test_empty_vault_returns_empty_dict(self, vault_dir):
        assert namespace_summary(vault_dir) == {}
