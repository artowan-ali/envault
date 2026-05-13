"""Tests for envault.acl module."""

import pytest
from pathlib import Path
from envault.acl import (
    set_permission,
    remove_permission,
    get_permissions,
    has_permission,
    list_acl,
    list_all_acl,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetPermission:
    def test_set_single_permission(self, vault_dir):
        set_permission(vault_dir, "DB_PASS", "alice", ["read"])
        assert get_permissions(vault_dir, "DB_PASS", "alice") == ["read"]

    def test_set_multiple_permissions(self, vault_dir):
        set_permission(vault_dir, "API_KEY", "bob", ["read", "write"])
        perms = get_permissions(vault_dir, "API_KEY", "bob")
        assert "read" in perms
        assert "write" in perms

    def test_permissions_are_sorted(self, vault_dir):
        set_permission(vault_dir, "X", "carol", ["write", "read", "delete"])
        assert get_permissions(vault_dir, "X", "carol") == ["delete", "read", "write"]

    def test_invalid_permission_raises(self, vault_dir):
        with pytest.raises(ValueError, match="Invalid permissions"):
            set_permission(vault_dir, "KEY", "alice", ["admin"])

    def test_overwrite_existing_permissions(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read", "write"])
        set_permission(vault_dir, "KEY", "alice", ["read"])
        assert get_permissions(vault_dir, "KEY", "alice") == ["read"]

    def test_multiple_users_on_same_key(self, vault_dir):
        set_permission(vault_dir, "SECRET", "alice", ["read"])
        set_permission(vault_dir, "SECRET", "bob", ["read", "write"])
        assert get_permissions(vault_dir, "SECRET", "alice") == ["read"]
        assert "write" in get_permissions(vault_dir, "SECRET", "bob")


class TestHasPermission:
    def test_has_granted_permission(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        assert has_permission(vault_dir, "KEY", "alice", "read") is True

    def test_missing_permission_returns_false(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        assert has_permission(vault_dir, "KEY", "alice", "write") is False

    def test_unknown_user_returns_false(self, vault_dir):
        assert has_permission(vault_dir, "KEY", "nobody", "read") is False


class TestRemovePermission:
    def test_remove_existing_returns_true(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        assert remove_permission(vault_dir, "KEY", "alice") is True

    def test_remove_clears_permissions(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        remove_permission(vault_dir, "KEY", "alice")
        assert get_permissions(vault_dir, "KEY", "alice") == []

    def test_remove_missing_returns_false(self, vault_dir):
        assert remove_permission(vault_dir, "KEY", "ghost") is False

    def test_remove_last_user_removes_key_entry(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        remove_permission(vault_dir, "KEY", "alice")
        assert list_acl(vault_dir, "KEY") == {}


class TestListAcl:
    def test_list_returns_user_mapping(self, vault_dir):
        set_permission(vault_dir, "DB", "alice", ["read"])
        set_permission(vault_dir, "DB", "bob", ["write"])
        mapping = list_acl(vault_dir, "DB")
        assert "alice" in mapping
        assert "bob" in mapping

    def test_list_all_returns_all_keys(self, vault_dir):
        set_permission(vault_dir, "KEY1", "alice", ["read"])
        set_permission(vault_dir, "KEY2", "bob", ["write"])
        all_acl = list_all_acl(vault_dir)
        assert "KEY1" in all_acl
        assert "KEY2" in all_acl

    def test_empty_vault_returns_empty(self, vault_dir):
        assert list_all_acl(vault_dir) == {}
