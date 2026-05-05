"""Tests for envault.cli_audit module."""

import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.audit import record_event
from envault.cli_audit import cmd_audit_log, register_audit_commands


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def make_args(vault_dir, key=None):
    args = argparse.Namespace()
    args.vault_dir = str(vault_dir)
    args.key = key
    return args


class TestCmdAuditLog:
    def test_prints_no_entries_when_empty(self, vault_dir, capsys):
        cmd_audit_log(make_args(vault_dir))
        out = capsys.readouterr().out
        assert "No audit entries" in out

    def test_prints_log_entries(self, vault_dir, capsys):
        record_event(vault_dir, "set", "SECRET", user="alice")
        record_event(vault_dir, "get", "SECRET", user="bob")
        cmd_audit_log(make_args(vault_dir))
        out = capsys.readouterr().out
        assert "SECRET" in out
        assert "SET" in out
        assert "GET" in out

    def test_filters_by_key(self, vault_dir, capsys):
        record_event(vault_dir, "set", "KEY_A", user="alice")
        record_event(vault_dir, "set", "KEY_B", user="alice")
        cmd_audit_log(make_args(vault_dir, key="KEY_A"))
        out = capsys.readouterr().out
        assert "KEY_A" in out
        assert "KEY_B" not in out

    def test_filter_no_match_prints_message(self, vault_dir, capsys):
        record_event(vault_dir, "set", "KEY_A")
        cmd_audit_log(make_args(vault_dir, key="MISSING"))
        out = capsys.readouterr().out
        assert "No audit entries found for key: MISSING" in out

    def test_missing_vault_dir_prints_error(self, tmp_path, capsys):
        nonexistent = tmp_path / "no_such_dir"
        cmd_audit_log(make_args(nonexistent))
        out = capsys.readouterr().out
        assert "not found" in out


class TestRegisterAuditCommands:
    def test_audit_subcommand_registered(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_audit_commands(subparsers)
        args = parser.parse_args(["audit"])
        assert hasattr(args, "func")
        assert args.func == cmd_audit_log

    def test_audit_key_option(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_audit_commands(subparsers)
        args = parser.parse_args(["audit", "--key", "MY_KEY"])
        assert args.key == "MY_KEY"
