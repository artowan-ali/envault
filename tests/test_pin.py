"""Tests for envault.pin module."""

import time
import pytest
from unittest.mock import patch

from envault.pin import set_pin, verify_pin, remove_pin, pin_status


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndVerifyPin:
    def test_set_and_verify_correct_pin(self, vault_dir):
        set_pin(vault_dir, "1234")
        assert verify_pin(vault_dir, "1234") is True

    def test_wrong_pin_returns_false(self, vault_dir):
        set_pin(vault_dir, "1234")
        assert verify_pin(vault_dir, "0000") is False

    def test_no_pin_set_returns_false(self, vault_dir):
        assert verify_pin(vault_dir, "1234") is False

    def test_overwrite_pin(self, vault_dir):
        set_pin(vault_dir, "1234")
        set_pin(vault_dir, "5678")
        assert verify_pin(vault_dir, "5678") is True
        assert verify_pin(vault_dir, "1234") is False

    def test_expired_pin_returns_false(self, vault_dir):
        set_pin(vault_dir, "1234")
        future = time.time() + 7200  # 2 hours ahead
        with patch("envault.pin.time") as mock_time:
            mock_time.time.return_value = future
            assert verify_pin(vault_dir, "1234") is False


class TestRemovePin:
    def test_remove_existing_pin(self, vault_dir):
        set_pin(vault_dir, "1234")
        result = remove_pin(vault_dir)
        assert result is True

    def test_remove_nonexistent_pin_returns_false(self, vault_dir):
        result = remove_pin(vault_dir)
        assert result is False

    def test_verify_after_remove_returns_false(self, vault_dir):
        set_pin(vault_dir, "1234")
        remove_pin(vault_dir)
        assert verify_pin(vault_dir, "1234") is False


class TestPinStatus:
    def test_status_when_not_set(self, vault_dir):
        status = pin_status(vault_dir)
        assert status["set"] is False

    def test_status_when_set(self, vault_dir):
        set_pin(vault_dir, "1234")
        status = pin_status(vault_dir)
        assert status["set"] is True
        assert status["expired"] is False
        assert status["ttl_seconds"] == 3600

    def test_status_shows_expired(self, vault_dir):
        set_pin(vault_dir, "1234")
        future = time.time() + 7200
        with patch("envault.pin.time") as mock_time:
            mock_time.time.return_value = future
            status = pin_status(vault_dir)
        assert status["expired"] is True

    def test_age_approximately_zero_after_set(self, vault_dir):
        set_pin(vault_dir, "1234")
        status = pin_status(vault_dir)
        assert status["age_seconds"] < 5
