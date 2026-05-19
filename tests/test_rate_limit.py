"""Tests for envault.rate_limit."""

import time
import pytest

from envault.rate_limit import (
    check_rate_limit,
    get_rate_limit,
    list_rate_limits,
    remove_rate_limit,
    reset_calls,
    set_rate_limit,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndGetRateLimit:
    def test_set_and_get(self, vault_dir):
        set_rate_limit(vault_dir, "get", 10, 60)
        entry = get_rate_limit(vault_dir, "get")
        assert entry["max_calls"] == 10
        assert entry["window_seconds"] == 60

    def test_missing_operation_returns_none(self, vault_dir):
        assert get_rate_limit(vault_dir, "nonexistent") is None

    def test_overwrite_existing(self, vault_dir):
        set_rate_limit(vault_dir, "set", 5, 30)
        set_rate_limit(vault_dir, "set", 20, 120)
        entry = get_rate_limit(vault_dir, "set")
        assert entry["max_calls"] == 20
        assert entry["window_seconds"] == 120

    def test_initial_calls_empty(self, vault_dir):
        set_rate_limit(vault_dir, "delete", 3, 10)
        entry = get_rate_limit(vault_dir, "delete")
        assert entry["calls"] == []


class TestCheckRateLimit:
    def test_no_config_always_allowed(self, vault_dir):
        allowed, retry = check_rate_limit(vault_dir, "anything")
        assert allowed is True
        assert retry == 0

    def test_within_limit_allowed(self, vault_dir):
        set_rate_limit(vault_dir, "op", 3, 60)
        for _ in range(3):
            allowed, retry = check_rate_limit(vault_dir, "op")
            assert allowed is True
            assert retry == 0

    def test_exceeds_limit_denied(self, vault_dir):
        set_rate_limit(vault_dir, "op", 2, 60)
        check_rate_limit(vault_dir, "op")
        check_rate_limit(vault_dir, "op")
        allowed, retry = check_rate_limit(vault_dir, "op")
        assert allowed is False
        assert retry > 0

    def test_retry_after_is_positive(self, vault_dir):
        set_rate_limit(vault_dir, "op", 1, 30)
        check_rate_limit(vault_dir, "op")
        allowed, retry = check_rate_limit(vault_dir, "op")
        assert not allowed
        assert 0 < retry <= 31

    def test_calls_outside_window_pruned(self, vault_dir):
        set_rate_limit(vault_dir, "op", 1, 1)
        check_rate_limit(vault_dir, "op")  # uses up the 1 call
        time.sleep(1.1)
        allowed, retry = check_rate_limit(vault_dir, "op")
        assert allowed is True


class TestRemoveRateLimit:
    def test_remove_existing(self, vault_dir):
        set_rate_limit(vault_dir, "op", 5, 60)
        result = remove_rate_limit(vault_dir, "op")
        assert result is True
        assert get_rate_limit(vault_dir, "op") is None

    def test_remove_missing_returns_false(self, vault_dir):
        assert remove_rate_limit(vault_dir, "ghost") is False


class TestListRateLimits:
    def test_empty_returns_empty_dict(self, vault_dir):
        assert list_rate_limits(vault_dir) == {}

    def test_lists_all_operations(self, vault_dir):
        set_rate_limit(vault_dir, "get", 10, 60)
        set_rate_limit(vault_dir, "set", 5, 30)
        limits = list_rate_limits(vault_dir)
        assert "get" in limits
        assert "set" in limits


class TestResetCalls:
    def test_reset_clears_call_history(self, vault_dir):
        set_rate_limit(vault_dir, "op", 2, 60)
        check_rate_limit(vault_dir, "op")
        check_rate_limit(vault_dir, "op")
        reset_calls(vault_dir, "op")
        entry = get_rate_limit(vault_dir, "op")
        assert entry["calls"] == []

    def test_reset_missing_returns_false(self, vault_dir):
        assert reset_calls(vault_dir, "ghost") is False

    def test_reset_allows_calls_again(self, vault_dir):
        set_rate_limit(vault_dir, "op", 1, 60)
        check_rate_limit(vault_dir, "op")
        reset_calls(vault_dir, "op")
        allowed, _ = check_rate_limit(vault_dir, "op")
        assert allowed is True
