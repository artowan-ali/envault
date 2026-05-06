"""Tests for envault.ttl module."""

import time
import pytest
from pathlib import Path

from envault.ttl import (
    set_ttl, remove_ttl, get_expiry, is_expired, purge_expired, ttl_summary
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


class TestSetAndGetExpiry:
    def test_set_creates_ttl_entry(self, vault_dir):
        set_ttl(vault_dir, "MY_KEY", 60)
        expiry = get_expiry(vault_dir, "MY_KEY")
        assert expiry is not None

    def test_expiry_is_approximately_correct(self, vault_dir):
        before = time.time()
        set_ttl(vault_dir, "MY_KEY", 100)
        expiry = get_expiry(vault_dir, "MY_KEY")
        assert before + 99 < expiry < before + 102

    def test_missing_key_returns_none(self, vault_dir):
        assert get_expiry(vault_dir, "MISSING") is None


class TestIsExpired:
    def test_not_expired_for_future_ttl(self, vault_dir):
        set_ttl(vault_dir, "KEY", 3600)
        assert is_expired(vault_dir, "KEY") is False

    def test_expired_for_past_ttl(self, vault_dir):
        set_ttl(vault_dir, "KEY", -1)
        assert is_expired(vault_dir, "KEY") is True

    def test_no_ttl_is_not_expired(self, vault_dir):
        assert is_expired(vault_dir, "NO_TTL_KEY") is False


class TestRemoveTTL:
    def test_remove_clears_entry(self, vault_dir):
        set_ttl(vault_dir, "KEY", 60)
        remove_ttl(vault_dir, "KEY")
        assert get_expiry(vault_dir, "KEY") is None

    def test_remove_nonexistent_does_not_raise(self, vault_dir):
        remove_ttl(vault_dir, "GHOST")


class TestPurgeExpired:
    def test_returns_expired_keys(self, vault_dir):
        set_ttl(vault_dir, "OLD", -1)
        set_ttl(vault_dir, "NEW", 3600)
        expired = purge_expired(vault_dir)
        assert "OLD" in expired
        assert "NEW" not in expired

    def test_returns_empty_when_none_expired(self, vault_dir):
        set_ttl(vault_dir, "FRESH", 3600)
        assert purge_expired(vault_dir) == []


class TestTTLSummary:
    def test_summary_contains_all_keys(self, vault_dir):
        set_ttl(vault_dir, "A", 60)
        set_ttl(vault_dir, "B", 120)
        summary = ttl_summary(vault_dir)
        keys = [e["key"] for e in summary]
        assert "A" in keys
        assert "B" in keys

    def test_summary_has_required_fields(self, vault_dir):
        set_ttl(vault_dir, "X", 30)
        entry = ttl_summary(vault_dir)[0]
        assert "key" in entry
        assert "expiry" in entry
        assert "remaining" in entry

    def test_expired_key_has_zero_remaining(self, vault_dir):
        set_ttl(vault_dir, "OLD", -10)
        summary = ttl_summary(vault_dir)
        entry = next(e for e in summary if e["key"] == "OLD")
        assert entry["remaining"] == 0.0
