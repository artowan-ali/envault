"""Tests for envault.expiry_notify."""

import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.ttl import set_ttl
from envault.expiry_notify import (
    get_expiring_keys,
    get_expired_keys,
    notify_expiring_keys,
    expiry_summary,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


class TestGetExpiringKeys:
    def test_returns_empty_when_no_ttl(self, vault_dir):
        result = get_expiring_keys(vault_dir)
        assert result == []

    def test_detects_key_expiring_within_window(self, vault_dir):
        set_ttl(vault_dir, "API_KEY", 3600)  # expires in 1 hour
        result = get_expiring_keys(vault_dir, within_seconds=7200)
        assert any(e["key"] == "API_KEY" for e in result)

    def test_excludes_key_outside_window(self, vault_dir):
        set_ttl(vault_dir, "API_KEY", 9000)  # expires in 2.5 hours
        result = get_expiring_keys(vault_dir, within_seconds=3600)
        assert result == []

    def test_marks_expired_key(self, vault_dir):
        set_ttl(vault_dir, "OLD_KEY", -10)  # already expired
        result = get_expiring_keys(vault_dir, within_seconds=0)
        assert any(e["key"] == "OLD_KEY" and e["expired"] for e in result)

    def test_results_sorted_by_expiry(self, vault_dir):
        set_ttl(vault_dir, "B_KEY", 7200)
        set_ttl(vault_dir, "A_KEY", 3600)
        result = get_expiring_keys(vault_dir, within_seconds=86400)
        keys = [e["key"] for e in result]
        assert keys.index("A_KEY") < keys.index("B_KEY")


class TestGetExpiredKeys:
    def test_returns_only_expired(self, vault_dir):
        set_ttl(vault_dir, "LIVE_KEY", 3600)
        set_ttl(vault_dir, "DEAD_KEY", -1)
        result = get_expired_keys(vault_dir)
        assert all(e["expired"] for e in result)
        assert any(e["key"] == "DEAD_KEY" for e in result)
        assert not any(e["key"] == "LIVE_KEY" for e in result)


class TestNotifyExpiringKeys:
    def test_dispatches_expiring_event(self, vault_dir):
        set_ttl(vault_dir, "SOON_KEY", 100)
        with patch("envault.expiry_notify.dispatch_event") as mock_dispatch:
            result = notify_expiring_keys(vault_dir, within_seconds=3600)
        assert any(e["key"] == "SOON_KEY" for e in result)
        mock_dispatch.assert_called()
        call_args = mock_dispatch.call_args_list[0]
        assert call_args[0][1] == "key.expiring"

    def test_dispatches_expired_event(self, vault_dir):
        set_ttl(vault_dir, "OLD_KEY", -50)
        with patch("envault.expiry_notify.dispatch_event") as mock_dispatch:
            notify_expiring_keys(vault_dir, within_seconds=86400)
        events = [c[0][1] for c in mock_dispatch.call_args_list]
        assert "key.expired" in events

    def test_returns_empty_when_nothing_expiring(self, vault_dir):
        set_ttl(vault_dir, "FAR_KEY", 99999)
        result = notify_expiring_keys(vault_dir, within_seconds=60)
        assert result == []


class TestExpirySummary:
    def test_no_entries_message(self):
        assert expiry_summary([]) == "No keys are expiring soon."

    def test_expired_entry_shown(self):
        entries = [{"key": "OLD", "expiry": time.time() - 100, "time_left": -100, "expired": True}]
        summary = expiry_summary(entries)
        assert "OLD" in summary
        assert "EXPIRED" in summary

    def test_expiring_entry_shown(self):
        entries = [{"key": "SOON", "expiry": time.time() + 500, "time_left": 500, "expired": False}]
        summary = expiry_summary(entries)
        assert "SOON" in summary
        assert "expires in" in summary
