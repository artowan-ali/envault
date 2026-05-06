"""Tests for envault.cli_history commands."""

import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.vault import Vault
from envault.history import record_value
from envault.cli_history import cmd_history_show, cmd_history_clear, cmd_history_list


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


@pytest.fixture
def populated_vault(vault_dir):
    v = Vault(vault_dir, "testpass")
    v.set("DB_URL", "postgres://localhost/db")
    v.set("API_KEY", "secret123")
    return v


def make_args(vault_dir, **kwargs):
    args = argparse.Namespace(
        vault_dir=str(vault_dir),
        password="testpass",
        **kwargs,
    )
    return args


class TestCmdHistoryList:
    def test_prints_no_history_when_empty(self, vault_dir, capsys):
        args = make_args(vault_dir)
        cmd_history_list(args)
        out = capsys.readouterr().out
        assert "No history" in out

    def test_lists_keys_with_history(self, vault_dir, capsys):
        record_value(vault_dir, "MY_KEY", "enc_val")
        args = make_args(vault_dir)
        cmd_history_list(args)
        out = capsys.readouterr().out
        assert "MY_KEY" in out

    def test_shows_entry_count(self, vault_dir, capsys):
        record_value(vault_dir, "MY_KEY", "v1")
        record_value(vault_dir, "MY_KEY", "v2")
        args = make_args(vault_dir)
        cmd_history_list(args)
        out = capsys.readouterr().out
        assert "2" in out


class TestCmdHistoryClear:
    def test_clear_prints_confirmation(self, vault_dir, capsys):
        record_value(vault_dir, "KEY", "val")
        args = make_args(vault_dir, key="KEY")
        cmd_history_clear(args)
        out = capsys.readouterr().out
        assert "Cleared" in out
        assert "KEY" in out

    def test_clear_nonexistent_key_prints_message(self, vault_dir, capsys):
        args = make_args(vault_dir, key="GHOST")
        cmd_history_clear(args)
        out = capsys.readouterr().out
        assert "No history" in out


class TestCmdHistoryShow:
    def test_no_history_prints_message(self, vault_dir, populated_vault, capsys):
        args = make_args(vault_dir, key="DB_URL")
        cmd_history_show(args)
        out = capsys.readouterr().out
        assert "No history" in out

    def test_shows_entry_count_in_header(self, vault_dir, populated_vault, capsys):
        # Record an encrypted value from the vault
        raw = populated_vault._store.get("DB_URL")
        record_value(vault_dir, "DB_URL", raw)
        args = make_args(vault_dir, key="DB_URL")
        cmd_history_show(args)
        out = capsys.readouterr().out
        assert "DB_URL" in out
        assert "1 entries" in out
