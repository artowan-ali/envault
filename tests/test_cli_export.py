"""Tests for CLI export/import commands."""

import json
import os
import types
import pytest

from envault.vault import Vault
from envault.cli_export import cmd_export, cmd_import


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path / "vault")


@pytest.fixture
def populated_vault(vault_dir):
    v = Vault(vault_dir, "testpass")
    v.set("DB_HOST", "localhost")
    v.set("API_KEY", "secret123")
    return v


def make_args(**kwargs):
    args = types.SimpleNamespace(format=None, **kwargs)
    return args


class TestCmdExport:
    def test_export_env_format(self, tmp_path, populated_vault):
        out = str(tmp_path / "out.env")
        args = make_args(output=out)
        cmd_export(args, vault=populated_vault)
        assert os.path.exists(out)
        with open(out) as f:
            content = f.read()
        assert "DB_HOST" in content
        assert "API_KEY" in content

    def test_export_json_format(self, tmp_path, populated_vault):
        out = str(tmp_path / "out.json")
        args = make_args(output=out)
        cmd_export(args, vault=populated_vault)
        with open(out) as f:
            data = json.load(f)
        assert data["DB_HOST"] == "localhost"
        assert data["API_KEY"] == "secret123"

    def test_export_prints_count(self, tmp_path, populated_vault, capsys):
        out = str(tmp_path / "out.env")
        args = make_args(output=out)
        cmd_export(args, vault=populated_vault)
        captured = capsys.readouterr()
        assert "2 secret(s)" in captured.out

    def test_export_explicit_format_override(self, tmp_path, populated_vault):
        out = str(tmp_path / "myfile")
        args = make_args(output=out, format="json")
        cmd_export(args, vault=populated_vault)
        with open(out) as f:
            data = json.load(f)
        assert "DB_HOST" in data


class TestCmdImport:
    def test_import_env_file(self, tmp_path, vault_dir, capsys):
        env_file = str(tmp_path / "import.env")
        with open(env_file, "w") as f:
            f.write('NEW_KEY="newvalue"\n')
        vault = Vault(vault_dir, "testpass")
        args = make_args(input=env_file)
        cmd_import(args, vault=vault)
        assert vault.get("NEW_KEY") == "newvalue"

    def test_import_json_file(self, tmp_path, vault_dir):
        json_file = str(tmp_path / "import.json")
        with open(json_file, "w") as f:
            json.dump({"FOO": "bar"}, f)
        vault = Vault(vault_dir, "testpass")
        args = make_args(input=json_file)
        cmd_import(args, vault=vault)
        assert vault.get("FOO") == "bar"

    def test_import_reports_new_and_overwritten(self, tmp_path, vault_dir, capsys):
        vault = Vault(vault_dir, "testpass")
        vault.set("EXISTING", "old")
        json_file = str(tmp_path / "import.json")
        with open(json_file, "w") as f:
            json.dump({"EXISTING": "new", "FRESH": "val"}, f)
        args = make_args(input=json_file)
        cmd_import(args, vault=vault)
        captured = capsys.readouterr()
        assert "1 new" in captured.out
        assert "1 overwritten" in captured.out

    def test_import_missing_file_exits(self, tmp_path, vault_dir):
        vault = Vault(vault_dir, "testpass")
        args = make_args(input=str(tmp_path / "nonexistent.env"))
        with pytest.raises(SystemExit):
            cmd_import(args, vault=vault)
