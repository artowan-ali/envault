"""Tests for envault.webhook module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from envault.webhook import register_webhook, remove_webhook, list_webhooks, fire_event


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestRegisterWebhook:
    def test_register_creates_entry(self, vault_dir):
        register_webhook(vault_dir, "slack", "https://example.com/hook")
        hooks = list_webhooks(vault_dir)
        assert "slack" in hooks
        assert hooks["slack"]["url"] == "https://example.com/hook"

    def test_default_events_is_wildcard(self, vault_dir):
        register_webhook(vault_dir, "slack", "https://example.com/hook")
        hooks = list_webhooks(vault_dir)
        assert hooks["slack"]["events"] == ["*"]

    def test_custom_events_stored(self, vault_dir):
        register_webhook(vault_dir, "ci", "https://ci.example.com", ["set", "delete"])
        hooks = list_webhooks(vault_dir)
        assert hooks["ci"]["events"] == ["set", "delete"]

    def test_overwrite_existing(self, vault_dir):
        register_webhook(vault_dir, "hook", "https://old.example.com")
        register_webhook(vault_dir, "hook", "https://new.example.com")
        hooks = list_webhooks(vault_dir)
        assert hooks["hook"]["url"] == "https://new.example.com"


class TestRemoveWebhook:
    def test_remove_existing_returns_true(self, vault_dir):
        register_webhook(vault_dir, "hook", "https://example.com")
        assert remove_webhook(vault_dir, "hook") is True
        assert "hook" not in list_webhooks(vault_dir)

    def test_remove_missing_returns_false(self, vault_dir):
        assert remove_webhook(vault_dir, "nonexistent") is False


class TestListWebhooks:
    def test_empty_when_no_webhooks(self, vault_dir):
        assert list_webhooks(vault_dir) == {}

    def test_lists_all_registered(self, vault_dir):
        register_webhook(vault_dir, "a", "https://a.example.com")
        register_webhook(vault_dir, "b", "https://b.example.com")
        hooks = list_webhooks(vault_dir)
        assert set(hooks.keys()) == {"a", "b"}


class TestFireEvent:
    def test_fires_wildcard_hook(self, vault_dir):
        register_webhook(vault_dir, "hook", "https://example.com/hook")
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            results = fire_event(vault_dir, "set", {"key": "FOO"})
        assert len(results) == 1
        assert results[0]["status"] == 200
        assert results[0]["error"] is None

    def test_skips_non_matching_event(self, vault_dir):
        register_webhook(vault_dir, "hook", "https://example.com", ["delete"])
        results = fire_event(vault_dir, "set", {"key": "FOO"})
        assert results == []

    def test_error_captured_in_result(self, vault_dir):
        import urllib.error
        register_webhook(vault_dir, "hook", "https://unreachable.example.com")
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
            results = fire_event(vault_dir, "set", {"key": "FOO"})
        assert results[0]["error"] is not None
        assert results[0]["status"] is None
