"""Tests for envault.cli_rate_limit."""

import pytest

from envault.cli_rate_limit import (
    cmd_ratelimit_check,
    cmd_ratelimit_list,
    cmd_ratelimit_remove,
    cmd_ratelimit_reset,
    cmd_ratelimit_set,
    cmd_ratelimit_show,
)
from envault.rate_limit import check_rate_limit, set_rate_limit


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def make_args(**kwargs):
    class Args:
        pass
    a = Args()
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


class TestCmdRatelimitSet:
    def test_set_prints_confirmation(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, operation="get", max_calls=10, window=60)
        cmd_ratelimit_set(args)
        out = capsys.readouterr().out
        assert "get" in out
        assert "10" in out
        assert "60" in out


class TestCmdRatelimitRemove:
    def test_remove_existing(self, vault_dir, capsys):
        set_rate_limit(vault_dir, "op", 5, 30)
        args = make_args(vault_dir=vault_dir, operation="op")
        cmd_ratelimit_remove(args)
        out = capsys.readouterr().out
        assert "removed" in out.lower()

    def test_remove_missing(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, operation="ghost")
        cmd_ratelimit_remove(args)
        out = capsys.readouterr().out
        assert "no rate limit" in out.lower()


class TestCmdRatelimitCheck:
    def test_allowed_message(self, vault_dir, capsys):
        set_rate_limit(vault_dir, "op", 5, 60)
        args = make_args(vault_dir=vault_dir, operation="op")
        cmd_ratelimit_check(args)
        out = capsys.readouterr().out
        assert "allowed" in out.lower()

    def test_denied_message(self, vault_dir, capsys):
        set_rate_limit(vault_dir, "op", 1, 60)
        check_rate_limit(vault_dir, "op")  # exhaust limit
        args = make_args(vault_dir=vault_dir, operation="op")
        cmd_ratelimit_check(args)
        out = capsys.readouterr().out
        assert "denied" in out.lower()
        assert "retry" in out.lower()


class TestCmdRatelimitShow:
    def test_show_existing(self, vault_dir, capsys):
        set_rate_limit(vault_dir, "delete", 3, 10)
        args = make_args(vault_dir=vault_dir, operation="delete")
        cmd_ratelimit_show(args)
        out = capsys.readouterr().out
        assert "delete" in out
        assert "3" in out
        assert "10" in out

    def test_show_missing(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, operation="none")
        cmd_ratelimit_show(args)
        out = capsys.readouterr().out
        assert "no rate limit" in out.lower()


class TestCmdRatelimitList:
    def test_empty(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir)
        cmd_ratelimit_list(args)
        out = capsys.readouterr().out
        assert "no rate limits" in out.lower()

    def test_lists_operations(self, vault_dir, capsys):
        set_rate_limit(vault_dir, "get", 10, 60)
        set_rate_limit(vault_dir, "set", 5, 30)
        args = make_args(vault_dir=vault_dir)
        cmd_ratelimit_list(args)
        out = capsys.readouterr().out
        assert "get" in out
        assert "set" in out


class TestCmdRatelimitReset:
    def test_reset_existing(self, vault_dir, capsys):
        set_rate_limit(vault_dir, "op", 2, 60)
        args = make_args(vault_dir=vault_dir, operation="op")
        cmd_ratelimit_reset(args)
        out = capsys.readouterr().out
        assert "reset" in out.lower()

    def test_reset_missing(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, operation="ghost")
        cmd_ratelimit_reset(args)
        out = capsys.readouterr().out
        assert "no rate limit" in out.lower()
