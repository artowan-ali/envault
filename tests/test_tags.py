"""Tests for envault/tags.py"""

from __future__ import annotations

import pytest

from envault import tags as tag_mod


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


class TestAddTag:
    def test_add_single_tag(self, vault_dir):
        tag_mod.add_tag(vault_dir, "DB_URL", "database")
        assert "database" in tag_mod.get_tags(vault_dir, "DB_URL")

    def test_add_multiple_tags(self, vault_dir):
        tag_mod.add_tag(vault_dir, "DB_URL", "database")
        tag_mod.add_tag(vault_dir, "DB_URL", "production")
        t = tag_mod.get_tags(vault_dir, "DB_URL")
        assert "database" in t
        assert "production" in t

    def test_duplicate_tag_not_added_twice(self, vault_dir):
        tag_mod.add_tag(vault_dir, "KEY", "infra")
        tag_mod.add_tag(vault_dir, "KEY", "infra")
        assert tag_mod.get_tags(vault_dir, "KEY").count("infra") == 1

    def test_tags_are_sorted(self, vault_dir):
        tag_mod.add_tag(vault_dir, "KEY", "zebra")
        tag_mod.add_tag(vault_dir, "KEY", "alpha")
        assert tag_mod.get_tags(vault_dir, "KEY") == ["alpha", "zebra"]


class TestRemoveTag:
    def test_remove_existing_tag(self, vault_dir):
        tag_mod.add_tag(vault_dir, "KEY", "old")
        result = tag_mod.remove_tag(vault_dir, "KEY", "old")
        assert result is True
        assert "old" not in tag_mod.get_tags(vault_dir, "KEY")

    def test_remove_nonexistent_tag_returns_false(self, vault_dir):
        result = tag_mod.remove_tag(vault_dir, "KEY", "ghost")
        assert result is False

    def test_key_removed_when_no_tags_remain(self, vault_dir):
        tag_mod.add_tag(vault_dir, "KEY", "solo")
        tag_mod.remove_tag(vault_dir, "KEY", "solo")
        raw = tag_mod._load_tags(vault_dir)
        assert "KEY" not in raw


class TestKeysForTag:
    def test_returns_keys_with_tag(self, vault_dir):
        tag_mod.add_tag(vault_dir, "A", "shared")
        tag_mod.add_tag(vault_dir, "B", "shared")
        tag_mod.add_tag(vault_dir, "C", "other")
        assert tag_mod.keys_for_tag(vault_dir, "shared") == ["A", "B"]

    def test_returns_empty_for_unknown_tag(self, vault_dir):
        assert tag_mod.keys_for_tag(vault_dir, "nope") == []


class TestAllTags:
    def test_returns_all_distinct_tags(self, vault_dir):
        tag_mod.add_tag(vault_dir, "X", "alpha")
        tag_mod.add_tag(vault_dir, "Y", "beta")
        tag_mod.add_tag(vault_dir, "Z", "alpha")
        assert tag_mod.all_tags(vault_dir) == ["alpha", "beta"]

    def test_empty_vault_returns_empty(self, vault_dir):
        assert tag_mod.all_tags(vault_dir) == []


class TestTagsSummary:
    def test_no_tags_message(self, vault_dir):
        assert tag_mod.tags_summary(vault_dir) == "No tags defined."

    def test_summary_contains_key_and_tag(self, vault_dir):
        tag_mod.add_tag(vault_dir, "API_KEY", "secret")
        summary = tag_mod.tags_summary(vault_dir)
        assert "API_KEY" in summary
        assert "secret" in summary
