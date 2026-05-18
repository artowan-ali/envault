"""Tests for envault.quota module."""

import pytest
from pathlib import Path
from envault.quota import (
    set_quota,
    remove_quota,
    get_quota,
    list_quotas,
    check_quota,
    quota_summary,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndGetQuota:
    def test_set_and_get(self, vault_dir):
        set_quota(vault_dir, "global", 100)
        assert get_quota(vault_dir, "global") == 100

    def test_missing_scope_returns_none(self, vault_dir):
        assert get_quota(vault_dir, "nonexistent") is None

    def test_overwrite_existing_quota(self, vault_dir):
        set_quota(vault_dir, "global", 50)
        set_quota(vault_dir, "global", 200)
        assert get_quota(vault_dir, "global") == 200

    def test_invalid_limit_raises(self, vault_dir):
        with pytest.raises(ValueError):
            set_quota(vault_dir, "global", 0)

    def test_negative_limit_raises(self, vault_dir):
        with pytest.raises(ValueError):
            set_quota(vault_dir, "global", -5)

    def test_multiple_scopes(self, vault_dir):
        set_quota(vault_dir, "global", 100)
        set_quota(vault_dir, "prod", 20)
        assert get_quota(vault_dir, "global") == 100
        assert get_quota(vault_dir, "prod") == 20


class TestRemoveQuota:
    def test_remove_existing_returns_true(self, vault_dir):
        set_quota(vault_dir, "dev", 10)
        assert remove_quota(vault_dir, "dev") is True
        assert get_quota(vault_dir, "dev") is None

    def test_remove_missing_returns_false(self, vault_dir):
        assert remove_quota(vault_dir, "missing") is False


class TestListQuotas:
    def test_empty_returns_empty_dict(self, vault_dir):
        assert list_quotas(vault_dir) == {}

    def test_lists_all_scopes(self, vault_dir):
        set_quota(vault_dir, "global", 100)
        set_quota(vault_dir, "staging", 30)
        result = list_quotas(vault_dir)
        assert result == {"global": 100, "staging": 30}


class TestCheckQuota:
    def test_within_limit_returns_true(self, vault_dir):
        set_quota(vault_dir, "global", 10)
        assert check_quota(vault_dir, "global", 5) is True

    def test_at_limit_returns_true(self, vault_dir):
        set_quota(vault_dir, "global", 10)
        assert check_quota(vault_dir, "global", 10) is True

    def test_over_limit_returns_false(self, vault_dir):
        set_quota(vault_dir, "global", 10)
        assert check_quota(vault_dir, "global", 11) is False

    def test_falls_back_to_global(self, vault_dir):
        set_quota(vault_dir, "global", 5)
        assert check_quota(vault_dir, "dev", 3) is True
        assert check_quota(vault_dir, "dev", 6) is False

    def test_no_quota_always_passes(self, vault_dir):
        assert check_quota(vault_dir, "any", 9999) is True


class TestQuotaSummary:
    def test_empty_summary(self, vault_dir):
        assert quota_summary(vault_dir) == "No quotas defined."

    def test_summary_contains_scopes(self, vault_dir):
        set_quota(vault_dir, "global", 100)
        set_quota(vault_dir, "prod", 25)
        summary = quota_summary(vault_dir)
        assert "global: 100 keys" in summary
        assert "prod: 25 keys" in summary
