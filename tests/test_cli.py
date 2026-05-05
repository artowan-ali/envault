"""Tests for the envault CLI."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

from envault.cli import build_parser, cmd_set, cmd_get, cmd_list, cmd_delete, main
from envault.vault import Vault


PASSWORD = "cli-test-password"


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path / "test_vault")


def make_args(vault_dir, command, **kwargs):
    """Build a simple namespace mimicking parsed args."""
    import argparse
    ns = argparse.Namespace(
        vault=vault_dir,
        password=PASSWORD,
        command=command,
        **kwargs,
    )
    return ns


class TestCmdSet:
    def test_set_creates_key(self, vault_dir):
        args = make_args(vault_dir, "set", key="DB_URL", value="postgres://localhost")
        cmd_set(args)
        vault = Vault(vault_dir, PASSWORD)
        assert vault.get("DB_URL") == "postgres://localhost"

    def test_set_prints_confirmation(self, vault_dir, capsys):
        args = make_args(vault_dir, "set", key="FOO", value="bar")
        cmd_set(args)
        captured = capsys.readouterr()
        assert "FOO" in captured.out


class TestCmdGet:
    def test_get_existing_key(self, vault_dir, capsys):
        args_set = make_args(vault_dir, "set", key="SECRET", value="abc123")
        cmd_set(args_set)
        args_get = make_args(vault_dir, "get", key="SECRET")
        cmd_get(args_get)
        captured = capsys.readouterr()
        assert "abc123" in captured.out

    def test_get_missing_key_exits(self, vault_dir):
        args = make_args(vault_dir, "get", key="MISSING")
        with pytest.raises(SystemExit) as exc:
            cmd_get(args)
        assert exc.value.code == 1


class TestCmdList:
    def test_list_empty_vault(self, vault_dir, capsys):
        args = make_args(vault_dir, "list")
        cmd_list(args)
        captured = capsys.readouterr()
        assert "empty" in captured.out.lower()

    def test_list_shows_keys(self, vault_dir, capsys):
        for k, v in [("ALPHA", "1"), ("BETA", "2")]:
            cmd_set(make_args(vault_dir, "set", key=k, value=v))
        cmd_list(make_args(vault_dir, "list"))
        captured = capsys.readouterr()
        assert "ALPHA" in captured.out
        assert "BETA" in captured.out


class TestCmdDelete:
    def test_delete_removes_key(self, vault_dir):
        cmd_set(make_args(vault_dir, "set", key="TO_DEL", value="gone"))
        cmd_delete(make_args(vault_dir, "delete", key="TO_DEL"))
        vault = Vault(vault_dir, PASSWORD)
        assert vault.get("TO_DEL") is None

    def test_delete_prints_confirmation(self, vault_dir, capsys):
        cmd_set(make_args(vault_dir, "set", key="TO_DEL", value="gone"))
        cmd_delete(make_args(vault_dir, "delete", key="TO_DEL"))
        captured = capsys.readouterr()
        assert "TO_DEL" in captured.out


class TestBuildParser:
    def test_parser_set_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["set", "KEY", "VALUE"])
        assert args.key == "KEY"
        assert args.value == "VALUE"

    def test_parser_get_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["get", "KEY"])
        assert args.key == "KEY"

    def test_parser_default_vault_path(self):
        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.vault == ".envault"

    def test_parser_custom_vault_path(self):
        parser = build_parser()
        args = parser.parse_args(["--vault", "/tmp/myvault", "list"])
        assert args.vault == "/tmp/myvault"
