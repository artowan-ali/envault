"""Tests for envault.snapshot."""

import time
import pytest
from pathlib import Path
from envault.snapshot import (
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
    list_snapshots,
    snapshot_summary,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


SAMPLE_STORE = {"DB_URL": "encrypted_abc", "API_KEY": "encrypted_xyz"}


class TestCreateSnapshot:
    def test_creates_snapshot_file(self, vault_dir):
        create_snapshot(vault_dir, "v1", SAMPLE_STORE)
        assert (Path(vault_dir) / "snapshots.json").exists()

    def test_returned_entry_has_name(self, vault_dir):
        entry = create_snapshot(vault_dir, "v1", SAMPLE_STORE)
        assert entry["name"] == "v1"

    def test_returned_entry_has_timestamp(self, vault_dir):
        before = time.time()
        entry = create_snapshot(vault_dir, "v1", SAMPLE_STORE)
        after = time.time()
        assert before <= entry["timestamp"] <= after

    def test_returned_entry_has_store(self, vault_dir):
        entry = create_snapshot(vault_dir, "v1", SAMPLE_STORE)
        assert entry["store"] == SAMPLE_STORE

    def test_overwrite_existing_snapshot(self, vault_dir):
        create_snapshot(vault_dir, "v1", SAMPLE_STORE)
        new_store = {"ONLY_KEY": "encrypted_new"}
        create_snapshot(vault_dir, "v1", new_store)
        restored = restore_snapshot(vault_dir, "v1")
        assert restored == new_store


class TestRestoreSnapshot:
    def test_restore_returns_correct_store(self, vault_dir):
        create_snapshot(vault_dir, "snap1", SAMPLE_STORE)
        result = restore_snapshot(vault_dir, "snap1")
        assert result == SAMPLE_STORE

    def test_restore_missing_returns_none(self, vault_dir):
        result = restore_snapshot(vault_dir, "nonexistent")
        assert result is None

    def test_restore_returns_copy(self, vault_dir):
        create_snapshot(vault_dir, "snap1", SAMPLE_STORE)
        result = restore_snapshot(vault_dir, "snap1")
        result["NEW_KEY"] = "val"
        assert restore_snapshot(vault_dir, "snap1") == SAMPLE_STORE


class TestDeleteSnapshot:
    def test_delete_existing_returns_true(self, vault_dir):
        create_snapshot(vault_dir, "snap1", SAMPLE_STORE)
        assert delete_snapshot(vault_dir, "snap1") is True

    def test_delete_removes_snapshot(self, vault_dir):
        create_snapshot(vault_dir, "snap1", SAMPLE_STORE)
        delete_snapshot(vault_dir, "snap1")
        assert restore_snapshot(vault_dir, "snap1") is None

    def test_delete_missing_returns_false(self, vault_dir):
        assert delete_snapshot(vault_dir, "ghost") is False


class TestListSnapshots:
    def test_empty_returns_empty_list(self, vault_dir):
        assert list_snapshots(vault_dir) == []

    def test_lists_all_snapshots(self, vault_dir):
        create_snapshot(vault_dir, "a", SAMPLE_STORE)
        create_snapshot(vault_dir, "b", SAMPLE_STORE)
        names = [e["name"] for e in list_snapshots(vault_dir)]
        assert set(names) == {"a", "b"}

    def test_sorted_by_timestamp(self, vault_dir):
        create_snapshot(vault_dir, "first", SAMPLE_STORE)
        time.sleep(0.01)
        create_snapshot(vault_dir, "second", SAMPLE_STORE)
        names = [e["name"] for e in list_snapshots(vault_dir)]
        assert names == ["first", "second"]


class TestSnapshotSummary:
    def test_no_snapshots_message(self, vault_dir):
        assert snapshot_summary(vault_dir) == "No snapshots found."

    def test_summary_contains_snapshot_name(self, vault_dir):
        create_snapshot(vault_dir, "release-1.0", SAMPLE_STORE)
        summary = snapshot_summary(vault_dir)
        assert "release-1.0" in summary
