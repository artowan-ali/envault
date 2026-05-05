"""Tests for envault.diff module."""

import json
import pytest

from envault.diff import (
    apply_diff,
    deserialize_diff,
    diff_summary,
    generate_diff,
    serialize_diff,
)


OLD_DATA = {
    "DB_URL": "enc_old_db",
    "SECRET_KEY": "enc_secret",
    "REMOVED_VAR": "enc_removed",
}

NEW_DATA = {
    "DB_URL": "enc_new_db",
    "SECRET_KEY": "enc_secret",
    "ADDED_VAR": "enc_added",
}


class TestGenerateDiff:
    def test_detects_added_keys(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        assert "ADDED_VAR" in diff["added"]
        assert diff["added"]["ADDED_VAR"] == "enc_added"

    def test_detects_removed_keys(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        assert "REMOVED_VAR" in diff["removed"]

    def test_detects_modified_keys(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        assert "DB_URL" in diff["modified"]
        assert diff["modified"]["DB_URL"]["old"] == "enc_old_db"
        assert diff["modified"]["DB_URL"]["new"] == "enc_new_db"

    def test_unchanged_keys_not_in_diff(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        assert "SECRET_KEY" not in diff["added"]
        assert "SECRET_KEY" not in diff["removed"]
        assert "SECRET_KEY" not in diff["modified"]

    def test_empty_diff_for_identical_data(self):
        diff = generate_diff(OLD_DATA, OLD_DATA)
        assert diff["added"] == {}
        assert diff["removed"] == {}
        assert diff["modified"] == {}


class TestApplyDiff:
    def test_apply_produces_new_data(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        result = apply_diff(OLD_DATA, diff)
        assert result == NEW_DATA

    def test_apply_does_not_mutate_base(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        original_copy = dict(OLD_DATA)
        apply_diff(OLD_DATA, diff)
        assert OLD_DATA == original_copy

    def test_apply_empty_diff_returns_same(self):
        empty_diff = {"added": {}, "removed": {}, "modified": {}}
        result = apply_diff(OLD_DATA, empty_diff)
        assert result == OLD_DATA


class TestSerializeDeserialize:
    def test_roundtrip(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        serialized = serialize_diff(diff)
        restored = deserialize_diff(serialized)
        assert restored == diff

    def test_serialized_is_valid_json(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        serialized = serialize_diff(diff)
        parsed = json.loads(serialized)
        assert isinstance(parsed, dict)

    def test_deserialize_invalid_raises(self):
        with pytest.raises(ValueError, match="missing"):
            deserialize_diff(json.dumps({"added": {}}))


class TestDiffSummary:
    def test_summary_with_changes(self):
        diff = generate_diff(OLD_DATA, NEW_DATA)
        summary = diff_summary(diff)
        assert "+1 added" in summary
        assert "-1 removed" in summary
        assert "~1 modified" in summary

    def test_summary_no_changes(self):
        diff = generate_diff(OLD_DATA, OLD_DATA)
        assert diff_summary(diff) == "no changes"
