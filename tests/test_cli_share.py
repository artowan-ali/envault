"""Tests for envault.cli_share module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from envault.vault import Vault
from envault.cli_share import cmd_share_export, cmd_share_import, register_share_commands
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def populated_vault(vault_dir):
    v = Vault(os.path.join(vault_dir, "source"), "vaultpass")
    v.set("FOO", "bar")
    v.set("BAZ", "qux")
    return v


def make_args(**kwargs):
    args = MagicMock()
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


class TestCmdShareExport:
    def test_creates_patch_file(self, populated_vault, vault_dir):
        args = make_args(
            vault_dir=os.path.join(vault_dir, "source"),
            base_dir=None,
        )
        passwords = iter(["vaultpass", "recippass", "recippass"])
        with patch("envault.cli_share.get_password", side_effect=lambda _: next(passwords)):
            cmd_share_export(args)
        patch_path = os.path.join(vault_dir, "source", "share.patch")
        assert os.path.exists(patch_path)

    def test_mismatched_recipient_passwords_exits(self, populated_vault, vault_dir, capsys):
        args = make_args(
            vault_dir=os.path.join(vault_dir, "source"),
            base_dir=None,
        )
        passwords = iter(["vaultpass", "pass1", "pass2"])
        with patch("envault.cli_share.get_password", side_effect=lambda _: next(passwords)):
            with pytest.raises(SystemExit) as exc:
                cmd_share_export(args)
        assert exc.value.code == 1

    def test_prints_patch_path(self, populated_vault, vault_dir, capsys):
        args = make_args(
            vault_dir=os.path.join(vault_dir, "source"),
            base_dir=None,
        )
        passwords = iter(["vaultpass", "recippass", "recippass"])
        with patch("envault.cli_share.get_password", side_effect=lambda _: next(passwords)):
            cmd_share_export(args)
        captured = capsys.readouterr()
        assert "share.patch" in captured.out


class TestCmdShareImport:
    def test_imports_keys_into_vault(self, populated_vault, vault_dir):
        source_dir = os.path.join(vault_dir, "source")
        export_args = make_args(vault_dir=source_dir, base_dir=None)
        passwords_export = iter(["vaultpass", "shared", "shared"])
        with patch("envault.cli_share.get_password", side_effect=lambda _: next(passwords_export)):
            cmd_share_export(export_args)

        target_dir = os.path.join(vault_dir, "target")
        os.makedirs(target_dir, exist_ok=True)
        patch_file = os.path.join(source_dir, "share.patch")
        import_args = make_args(patch_file=patch_file, vault_dir=target_dir)
        passwords_import = iter(["shared", "targetpass"])
        with patch("envault.cli_share.get_password", side_effect=lambda _: next(passwords_import)):
            cmd_share_import(import_args)

        target = Vault(target_dir, "targetpass")
        assert target.get("FOO") == "bar"
        assert target.get("BAZ") == "qux"

    def test_missing_patch_file_exits(self, vault_dir, capsys):
        args = make_args(
            patch_file=os.path.join(vault_dir, "nonexistent.patch"),
            vault_dir=vault_dir,
        )
        with patch("envault.cli_share.get_password", return_value="pass"):
            with pytest.raises(SystemExit) as exc:
                cmd_share_import(args)
        assert exc.value.code == 1


class TestRegisterShareCommands:
    def test_registers_share_export_and_import(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_share_commands(subparsers)
        args = parser.parse_args(["share-export"])
        assert hasattr(args, "func")
