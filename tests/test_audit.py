"""Tests for envault.audit module."""

import pytest
from pathlib import Path

from envault.audit import (
    record_event,
    get_log,
    get_log_for_key,
    format_log,
    AUDIT_FILENAME,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


class TestRecordEvent:
    def test_creates_audit_file(self, vault_dir):
        record_event(vault_dir, "set", "MY_KEY")
        assert (vault_dir / AUDIT_FILENAME).exists()

    def test_entry_has_required_fields(self, vault_dir):
        record_event(vault_dir, "set", "MY_KEY", user="alice")
        log = get_log(vault_dir)
        assert len(log) == 1
        entry = log[0]
        assert entry["action"] == "set"
        assert entry["key"] == "MY_KEY"
        assert entry["user"] == "alice"
        assert "timestamp" in entry

    def test_multiple_events_appended(self, vault_dir):
        record_event(vault_dir, "set", "KEY_A", user="alice")
        record_event(vault_dir, "get", "KEY_A", user="bob")
        record_event(vault_dir, "delete", "KEY_A", user="alice")
        log = get_log(vault_dir)
        assert len(log) == 3
        assert [e["action"] for e in log] == ["set", "get", "delete"]

    def test_different_keys_recorded(self, vault_dir):
        record_event(vault_dir, "set", "KEY_A")
        record_event(vault_dir, "set", "KEY_B")
        log = get_log(vault_dir)
        keys = {e["key"] for e in log}
        assert keys == {"KEY_A", "KEY_B"}


class TestGetLogForKey:
    def test_filters_by_key(self, vault_dir):
        record_event(vault_dir, "set", "KEY_A")
        record_event(vault_dir, "set", "KEY_B")
        record_event(vault_dir, "get", "KEY_A")
        entries = get_log_for_key(vault_dir, "KEY_A")
        assert len(entries) == 2
        assert all(e["key"] == "KEY_A" for e in entries)

    def test_returns_empty_for_unknown_key(self, vault_dir):
        record_event(vault_dir, "set", "KEY_A")
        entries = get_log_for_key(vault_dir, "NONEXISTENT")
        assert entries == []


class TestFormatLog:
    def test_empty_log_message(self, vault_dir):
        result = format_log([])
        assert "No audit entries" in result

    def test_format_contains_key_info(self, vault_dir):
        record_event(vault_dir, "set", "MY_KEY", user="alice")
        log = get_log(vault_dir)
        output = format_log(log)
        assert "MY_KEY" in output
        assert "SET" in output
        assert "alice" in output

    def test_format_multiple_lines(self, vault_dir):
        record_event(vault_dir, "set", "A", user="u")
        record_event(vault_dir, "get", "B", user="u")
        log = get_log(vault_dir)
        lines = format_log(log).splitlines()
        assert len(lines) == 2
