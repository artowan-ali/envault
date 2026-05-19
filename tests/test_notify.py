"""Tests for envault.notify."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envault.notify import _matches_event, _post_webhook, dispatch_event
from envault.webhook import register_webhook


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


# --- _matches_event ---

class TestMatchesEvent:
    def test_wildcard_matches_any(self):
        assert _matches_event(["*"], "set") is True

    def test_specific_event_matches(self):
        assert _matches_event(["set", "delete"], "set") is True

    def test_specific_event_no_match(self):
        assert _matches_event(["delete"], "set") is False

    def test_empty_list_no_match(self):
        assert _matches_event([], "set") is False


# --- _post_webhook ---

class TestPostWebhook:
    def test_returns_true_on_success(self):
        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_response):
            result = _post_webhook("http://example.com/hook", {"event": "set"})
        assert result is True

    def test_returns_false_on_url_error(self):
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("fail")):
            result = _post_webhook("http://bad.url/hook", {"event": "set"})
        assert result is False

    def test_returns_false_on_os_error(self):
        with patch("urllib.request.urlopen", side_effect=OSError("timeout")):
            result = _post_webhook("http://bad.url/hook", {"event": "set"})
        assert result is False


# --- dispatch_event ---

class TestDispatchEvent:
    def test_no_webhooks_returns_zero_counts(self, vault_dir):
        result = dispatch_event(vault_dir, "set")
        assert result["sent"] == 0
        assert result["failed"] == 0
        assert result["skipped"] == 0

    def test_matching_webhook_increments_sent(self, vault_dir):
        register_webhook(vault_dir, "http://example.com/hook", events=["set"])
        with patch("envault.notify._post_webhook", return_value=True):
            result = dispatch_event(vault_dir, "set")
        assert result["sent"] == 1
        assert result["failed"] == 0

    def test_non_matching_webhook_increments_skipped(self, vault_dir):
        register_webhook(vault_dir, "http://example.com/hook", events=["delete"])
        with patch("envault.notify._post_webhook", return_value=True):
            result = dispatch_event(vault_dir, "set")
        assert result["skipped"] == 1
        assert result["sent"] == 0

    def test_failed_post_increments_failed(self, vault_dir):
        register_webhook(vault_dir, "http://example.com/hook", events=["*"])
        with patch("envault.notify._post_webhook", return_value=False):
            result = dispatch_event(vault_dir, "set")
        assert result["failed"] == 1
        assert result["sent"] == 0

    def test_event_name_in_result(self, vault_dir):
        result = dispatch_event(vault_dir, "rotate")
        assert result["event"] == "rotate"

    def test_metadata_passed_to_post(self, vault_dir):
        register_webhook(vault_dir, "http://example.com/hook", events=["*"])
        captured = {}

        def fake_post(url, payload, timeout=5):
            captured.update(payload)
            return True

        with patch("envault.notify._post_webhook", side_effect=fake_post):
            dispatch_event(vault_dir, "set", metadata={"key": "DB_URL"})

        assert captured.get("key") == "DB_URL"
        assert captured.get("event") == "set"
