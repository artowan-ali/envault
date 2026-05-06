"""Tests for envault/cli_tags.py"""

from __future__ import annotations

import argparse
import pytest

from envault import tags as tag_mod
from envault.cli_tags import (
    cmd_tag_add,
    cmd_tag_remove,
    cmd_tag_list,
    cmd_tag_all,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def make_args(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


class TestCmdTagAdd:
    def test_adds_tag_and_prints_confirmation(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, key="DB_URL", tag="database")
        cmd_tag_add(args)
        out = capsys.readouterr().out
        assert "database" in out
        assert "DB_URL" in out
        assert "database" in tag_mod.get_tags(vault_dir, "DB_URL")


class TestCmdTagRemove:
    def test_removes_existing_tag(self, vault_dir, capsys):
        tag_mod.add_tag(vault_dir, "KEY", "old")
        args = make_args(vault_dir=vault_dir, key="KEY", tag="old")
        cmd_tag_remove(args)
        out = capsys.readouterr().out
        assert "removed" in out.lower()
        assert "old" not in tag_mod.get_tags(vault_dir, "KEY")

    def test_reports_missing_tag(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, key="KEY", tag="ghost")
        cmd_tag_remove(args)
        out = capsys.readouterr().out
        assert "not found" in out.lower()


class TestCmdTagList:
    def test_lists_all_tags_when_no_filter(self, vault_dir, capsys):
        tag_mod.add_tag(vault_dir, "API_KEY", "secret")
        args = make_args(vault_dir=vault_dir, tag=None)
        cmd_tag_list(args)
        out = capsys.readouterr().out
        assert "API_KEY" in out
        assert "secret" in out

    def test_filters_keys_by_tag(self, vault_dir, capsys):
        tag_mod.add_tag(vault_dir, "A", "prod")
        tag_mod.add_tag(vault_dir, "B", "dev")
        args = make_args(vault_dir=vault_dir, tag="prod")
        cmd_tag_list(args)
        out = capsys.readouterr().out
        assert "A" in out
        assert "B" not in out

    def test_reports_no_keys_for_unknown_tag(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir, tag="nope")
        cmd_tag_list(args)
        out = capsys.readouterr().out
        assert "no keys" in out.lower()


class TestCmdTagAll:
    def test_prints_all_tags(self, vault_dir, capsys):
        tag_mod.add_tag(vault_dir, "X", "alpha")
        tag_mod.add_tag(vault_dir, "Y", "beta")
        args = make_args(vault_dir=vault_dir)
        cmd_tag_all(args)
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out

    def test_empty_vault_message(self, vault_dir, capsys):
        args = make_args(vault_dir=vault_dir)
        cmd_tag_all(args)
        out = capsys.readouterr().out
        assert "no tags" in out.lower()
