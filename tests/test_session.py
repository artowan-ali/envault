"""Tests for envault.session"""

import time
from pathlib import Path

import pytest

from envault.session import (
    clear_session,
    load_session,
    save_session,
    session_status,
    DEFAULT_SESSION_TTL,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSaveAndLoadSession:
    def test_load_returns_password(self, vault_dir):
        save_session(vault_dir, "s3cr3t")
        assert load_session(vault_dir) == "s3cr3t"

    def test_missing_session_returns_none(self, vault_dir):
        assert load_session(vault_dir) is None

    def test_expired_session_returns_none(self, vault_dir):
        save_session(vault_dir, "s3cr3t", ttl=-1)
        assert load_session(vault_dir) is None

    def test_expired_session_removes_file(self, vault_dir):
        save_session(vault_dir, "s3cr3t", ttl=-1)
        load_session(vault_dir)
        assert not Path(vault_dir, ".session").exists()

    def test_session_file_has_restricted_permissions(self, vault_dir):
        save_session(vault_dir, "s3cr3t")
        mode = Path(vault_dir, ".session").stat().st_mode & 0o777
        assert mode == 0o600

    def test_custom_ttl_stored(self, vault_dir):
        save_session(vault_dir, "pass", ttl=60)
        status = session_status(vault_dir)
        assert status["remaining_seconds"] <= 60


class TestClearSession:
    def test_clear_removes_file(self, vault_dir):
        save_session(vault_dir, "s3cr3t")
        clear_session(vault_dir)
        assert not Path(vault_dir, ".session").exists()

    def test_clear_when_no_session_is_noop(self, vault_dir):
        clear_session(vault_dir)  # should not raise


class TestSessionStatus:
    def test_no_session_returns_inactive(self, vault_dir):
        status = session_status(vault_dir)
        assert status["active"] is False
        assert status["expires_at"] is None
        assert status["remaining_seconds"] is None

    def test_active_session_returns_true(self, vault_dir):
        save_session(vault_dir, "pass", ttl=300)
        status = session_status(vault_dir)
        assert status["active"] is True
        assert status["remaining_seconds"] > 0

    def test_remaining_seconds_is_approximate(self, vault_dir):
        save_session(vault_dir, "pass", ttl=120)
        status = session_status(vault_dir)
        assert 118 <= status["remaining_seconds"] <= 120

    def test_expired_session_reports_inactive(self, vault_dir):
        save_session(vault_dir, "pass", ttl=-5)
        status = session_status(vault_dir)
        assert status["active"] is False
