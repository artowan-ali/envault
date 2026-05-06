"""Tests for envault.history module."""

import time
import pytest
from pathlib import Path

from envault.history import (
    record_value,
    get_history,
    clear_history,
    list_keys_with_history,
    history_summary,
    MAX_HISTORY_PER_KEY,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


class TestRecordAndGetHistory:
    def test_empty_history_returns_empty_list(self, vault_dir):
        assert get_history(vault_dir, "MY_KEY") == []

    def test_record_creates_entry(self, vault_dir):
        record_value(vault_dir, "KEY", "enc_val_1")
        entries = get_history(vault_dir, "KEY")
        assert len(entries) == 1
        assert entries[0]["value"] == "enc_val_1"

    def test_multiple_entries_appended(self, vault_dir):
        record_value(vault_dir, "KEY", "enc_val_1")
        record_value(vault_dir, "KEY", "enc_val_2")
        entries = get_history(vault_dir, "KEY")
        assert len(entries) == 2
        assert entries[0]["value"] == "enc_val_1"
        assert entries[1]["value"] == "enc_val_2"

    def test_entry_has_timestamp(self, vault_dir):
        before = time.time()
        record_value(vault_dir, "KEY", "val")
        after = time.time()
        entry = get_history(vault_dir, "KEY")[0]
        assert before <= entry["timestamp"] <= after

    def test_entry_stores_note(self, vault_dir):
        record_value(vault_dir, "KEY", "val", note="initial set")
        entry = get_history(vault_dir, "KEY")[0]
        assert entry["note"] == "initial set"

    def test_different_keys_independent(self, vault_dir):
        record_value(vault_dir, "KEY_A", "val_a")
        record_value(vault_dir, "KEY_B", "val_b")
        assert len(get_history(vault_dir, "KEY_A")) == 1
        assert len(get_history(vault_dir, "KEY_B")) == 1

    def test_max_history_trimmed(self, vault_dir):
        for i in range(MAX_HISTORY_PER_KEY + 5):
            record_value(vault_dir, "KEY", f"val_{i}")
        entries = get_history(vault_dir, "KEY")
        assert len(entries) == MAX_HISTORY_PER_KEY
        assert entries[-1]["value"] == f"val_{MAX_HISTORY_PER_KEY + 4}"


class TestClearHistory:
    def test_clear_removes_entries(self, vault_dir):
        record_value(vault_dir, "KEY", "val")
        removed = clear_history(vault_dir, "KEY")
        assert removed == 1
        assert get_history(vault_dir, "KEY") == []

    def test_clear_nonexistent_key_returns_zero(self, vault_dir):
        assert clear_history(vault_dir, "GHOST") == 0

    def test_clear_only_affects_target_key(self, vault_dir):
        record_value(vault_dir, "KEY_A", "a")
        record_value(vault_dir, "KEY_B", "b")
        clear_history(vault_dir, "KEY_A")
        assert get_history(vault_dir, "KEY_B") != []


class TestListAndSummary:
    def test_list_empty_when_no_history(self, vault_dir):
        assert list_keys_with_history(vault_dir) == []

    def test_list_returns_keys_with_entries(self, vault_dir):
        record_value(vault_dir, "A", "v")
        record_value(vault_dir, "B", "v")
        keys = list_keys_with_history(vault_dir)
        assert set(keys) == {"A", "B"}

    def test_summary_none_for_missing_key(self, vault_dir):
        assert history_summary(vault_dir, "NONE") is None

    def test_summary_returns_correct_count(self, vault_dir):
        record_value(vault_dir, "K", "v1")
        record_value(vault_dir, "K", "v2")
        s = history_summary(vault_dir, "K")
        assert s["count"] == 2
        assert s["key"] == "K"
