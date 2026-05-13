"""Tests for envault.cli_acl module."""

import pytest
from unittest.mock import patch
from envault.acl import set_permission
from envault.cli_acl import (
    cmd_acl_set,
    cmd_acl_remove,
    cmd_acl_check,
    cmd_acl_list,
    cmd_acl_all,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def make_args(vault_dir, **kwargs):
    class Args:
        pass
    a = Args()
    a.vault_dir = vault_dir
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


class TestCmdAclSet:
    def test_set_prints_confirmation(self, vault_dir, capsys):
        args = make_args(vault_dir, key="DB_PASS", user="alice", permissions="read,write")
        cmd_acl_set(args)
        out = capsys.readouterr().out
        assert "alice" in out
        assert "DB_PASS" in out

    def test_invalid_permission_exits(self, vault_dir):
        args = make_args(vault_dir, key="KEY", user="alice", permissions="admin")
        with pytest.raises(SystemExit):
            cmd_acl_set(args)


class TestCmdAclRemove:
    def test_remove_existing_prints_confirmation(self, vault_dir, capsys):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        args = make_args(vault_dir, key="KEY", user="alice")
        cmd_acl_remove(args)
        out = capsys.readouterr().out
        assert "alice" in out
        assert "KEY" in out

    def test_remove_missing_prints_not_found(self, vault_dir, capsys):
        args = make_args(vault_dir, key="KEY", user="ghost")
        cmd_acl_remove(args)
        out = capsys.readouterr().out
        assert "No permissions" in out


class TestCmdAclCheck:
    def test_check_granted_permission(self, vault_dir, capsys):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        args = make_args(vault_dir, key="KEY", user="alice", permission="read")
        cmd_acl_check(args)
        out = capsys.readouterr().out
        assert "has" in out

    def test_check_missing_permission_exits(self, vault_dir):
        set_permission(vault_dir, "KEY", "alice", ["read"])
        args = make_args(vault_dir, key="KEY", user="alice", permission="write")
        with pytest.raises(SystemExit):
            cmd_acl_check(args)


class TestCmdAclList:
    def test_list_prints_users(self, vault_dir, capsys):
        set_permission(vault_dir, "DB", "alice", ["read"])
        set_permission(vault_dir, "DB", "bob", ["write"])
        args = make_args(vault_dir, key="DB")
        cmd_acl_list(args)
        out = capsys.readouterr().out
        assert "alice" in out
        assert "bob" in out

    def test_list_empty_key_prints_none(self, vault_dir, capsys):
        args = make_args(vault_dir, key="MISSING")
        cmd_acl_list(args)
        out = capsys.readouterr().out
        assert "No ACL" in out


class TestCmdAclAll:
    def test_all_prints_all_keys(self, vault_dir, capsys):
        set_permission(vault_dir, "KEY1", "alice", ["read"])
        set_permission(vault_dir, "KEY2", "bob", ["write"])
        args = make_args(vault_dir)
        cmd_acl_all(args)
        out = capsys.readouterr().out
        assert "KEY1" in out
        assert "KEY2" in out

    def test_all_empty_prints_no_entries(self, vault_dir, capsys):
        args = make_args(vault_dir)
        cmd_acl_all(args)
        out = capsys.readouterr().out
        assert "No ACL" in out
