"""Tests for envault.lock module."""

import time
import json
import pytest
from pathlib import Path

from envault.lock import (
    acquire_lock,
    release_lock,
    is_locked,
    lock_info,
    LOCK_FILENAME,
    LOCK_TIMEOUT,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestAcquireLock:
    def test_acquire_creates_lock_file(self, vault_dir):
        result = acquire_lock(vault_dir)
        assert result is True
        assert (Path(vault_dir) / LOCK_FILENAME).exists()

    def test_acquire_returns_false_when_already_locked(self, vault_dir):
        acquire_lock(vault_dir)
        result = acquire_lock(vault_dir)
        assert result is False

    def test_lock_file_contains_owner_and_timestamp(self, vault_dir):
        acquire_lock(vault_dir, owner="test-owner")
        data = json.loads((Path(vault_dir) / LOCK_FILENAME).read_text())
        assert data["owner"] == "test-owner"
        assert "acquired_at" in data

    def test_acquire_removes_stale_lock(self, vault_dir):
        stale = {"owner": "old", "acquired_at": time.time() - LOCK_TIMEOUT - 1}
        (Path(vault_dir) / LOCK_FILENAME).write_text(json.dumps(stale))
        result = acquire_lock(vault_dir, owner="new")
        assert result is True
        data = json.loads((Path(vault_dir) / LOCK_FILENAME).read_text())
        assert data["owner"] == "new"

    def test_acquire_removes_corrupt_lock(self, vault_dir):
        (Path(vault_dir) / LOCK_FILENAME).write_text("not-json")
        result = acquire_lock(vault_dir)
        assert result is True


class TestReleaseLock:
    def test_release_removes_lock_file(self, vault_dir):
        acquire_lock(vault_dir)
        result = release_lock(vault_dir)
        assert result is True
        assert not (Path(vault_dir) / LOCK_FILENAME).exists()

    def test_release_returns_false_when_no_lock(self, vault_dir):
        result = release_lock(vault_dir)
        assert result is False


class TestIsLocked:
    def test_returns_false_when_no_lock(self, vault_dir):
        assert is_locked(vault_dir) is False

    def test_returns_true_after_acquire(self, vault_dir):
        acquire_lock(vault_dir)
        assert is_locked(vault_dir) is True

    def test_returns_false_after_release(self, vault_dir):
        acquire_lock(vault_dir)
        release_lock(vault_dir)
        assert is_locked(vault_dir) is False

    def test_stale_lock_is_not_locked(self, vault_dir):
        stale = {"owner": "old", "acquired_at": time.time() - LOCK_TIMEOUT - 5}
        (Path(vault_dir) / LOCK_FILENAME).write_text(json.dumps(stale))
        assert is_locked(vault_dir) is False


class TestLockInfo:
    def test_returns_empty_dict_when_no_lock(self, vault_dir):
        assert lock_info(vault_dir) == {}

    def test_returns_lock_metadata(self, vault_dir):
        acquire_lock(vault_dir, owner="ci-pipeline")
        info = lock_info(vault_dir)
        assert info["owner"] == "ci-pipeline"
        assert "acquired_at" in info
