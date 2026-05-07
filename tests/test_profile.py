"""Tests for envault.profile module."""

import pytest
from pathlib import Path
from envault.profile import (
    set_profile_key,
    get_profile_key,
    delete_profile_key,
    list_profiles,
    get_profile,
    delete_profile,
    profile_summary,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndGetProfileKey:
    def test_set_and_get(self, vault_dir):
        set_profile_key(vault_dir, "dev", "DB_HOST", "localhost")
        assert get_profile_key(vault_dir, "dev", "DB_HOST") == "localhost"

    def test_missing_key_returns_none(self, vault_dir):
        assert get_profile_key(vault_dir, "dev", "MISSING") is None

    def test_missing_profile_returns_none(self, vault_dir):
        assert get_profile_key(vault_dir, "nonexistent", "KEY") is None

    def test_overwrite_key(self, vault_dir):
        set_profile_key(vault_dir, "dev", "API_URL", "http://old")
        set_profile_key(vault_dir, "dev", "API_URL", "http://new")
        assert get_profile_key(vault_dir, "dev", "API_URL") == "http://new"

    def test_multiple_profiles_independent(self, vault_dir):
        set_profile_key(vault_dir, "dev", "HOST", "dev-host")
        set_profile_key(vault_dir, "prod", "HOST", "prod-host")
        assert get_profile_key(vault_dir, "dev", "HOST") == "dev-host"
        assert get_profile_key(vault_dir, "prod", "HOST") == "prod-host"


class TestDeleteProfileKey:
    def test_delete_existing_key(self, vault_dir):
        set_profile_key(vault_dir, "dev", "KEY", "val")
        result = delete_profile_key(vault_dir, "dev", "KEY")
        assert result is True
        assert get_profile_key(vault_dir, "dev", "KEY") is None

    def test_delete_missing_key_returns_false(self, vault_dir):
        assert delete_profile_key(vault_dir, "dev", "NOPE") is False

    def test_empty_profile_removed_after_last_key(self, vault_dir):
        set_profile_key(vault_dir, "dev", "ONLY", "val")
        delete_profile_key(vault_dir, "dev", "ONLY")
        assert "dev" not in list_profiles(vault_dir)


class TestListProfiles:
    def test_empty_returns_empty_list(self, vault_dir):
        assert list_profiles(vault_dir) == []

    def test_returns_sorted_profile_names(self, vault_dir):
        set_profile_key(vault_dir, "staging", "K", "v")
        set_profile_key(vault_dir, "dev", "K", "v")
        set_profile_key(vault_dir, "prod", "K", "v")
        assert list_profiles(vault_dir) == ["dev", "prod", "staging"]


class TestGetProfile:
    def test_returns_all_keys(self, vault_dir):
        set_profile_key(vault_dir, "dev", "A", "1")
        set_profile_key(vault_dir, "dev", "B", "2")
        data = get_profile(vault_dir, "dev")
        assert data == {"A": "1", "B": "2"}

    def test_nonexistent_profile_returns_empty(self, vault_dir):
        assert get_profile(vault_dir, "ghost") == {}


class TestDeleteProfile:
    def test_delete_existing_profile(self, vault_dir):
        set_profile_key(vault_dir, "dev", "K", "v")
        assert delete_profile(vault_dir, "dev") is True
        assert list_profiles(vault_dir) == []

    def test_delete_nonexistent_profile_returns_false(self, vault_dir):
        assert delete_profile(vault_dir, "ghost") is False


class TestProfileSummary:
    def test_no_profiles(self, vault_dir):
        assert profile_summary(vault_dir) == "No profiles defined."

    def test_summary_lists_profiles_and_counts(self, vault_dir):
        set_profile_key(vault_dir, "dev", "A", "1")
        set_profile_key(vault_dir, "dev", "B", "2")
        set_profile_key(vault_dir, "prod", "X", "9")
        summary = profile_summary(vault_dir)
        assert "dev: 2 key(s)" in summary
        assert "prod: 1 key(s)" in summary
