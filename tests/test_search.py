"""Tests for envault.search module."""

import pytest
from envault.search import (
    search_keys,
    search_values,
    filter_by_prefix,
    search_summary,
)

SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "s3cr3t",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "info",
}


class TestSearchKeys:
    def test_glob_matches_prefix(self):
        result = search_keys(SAMPLE, "DB_*")
        assert result == ["DB_HOST", "DB_PORT"]

    def test_glob_matches_all(self):
        result = search_keys(SAMPLE, "*")
        assert len(result) == len(SAMPLE)

    def test_no_match_returns_empty(self):
        result = search_keys(SAMPLE, "MISSING_*")
        assert result == []

    def test_regex_match(self):
        result = search_keys(SAMPLE, r"^APP_", use_regex=True)
        assert result == ["APP_DEBUG", "APP_SECRET"]

    def test_results_are_sorted(self):
        result = search_keys(SAMPLE, "*")
        assert result == sorted(result)


class TestSearchValues:
    def test_glob_matches_value(self):
        result = search_values(SAMPLE, "local*")
        assert result == ["DB_HOST"]

    def test_regex_matches_value(self):
        result = search_values(SAMPLE, r"\d+", use_regex=True)
        assert "DB_PORT" in result

    def test_no_value_match(self):
        result = search_values(SAMPLE, "nonexistent")
        assert result == []


class TestFilterByPrefix:
    def test_filters_correctly(self):
        result = filter_by_prefix(SAMPLE, "APP_")
        assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}

    def test_preserves_values(self):
        result = filter_by_prefix(SAMPLE, "DB_")
        assert result["DB_HOST"] == "localhost"
        assert result["DB_PORT"] == "5432"

    def test_empty_prefix_returns_all(self):
        result = filter_by_prefix(SAMPLE, "")
        assert len(result) == len(SAMPLE)

    def test_no_match_returns_empty(self):
        result = filter_by_prefix(SAMPLE, "NOPE_")
        assert result == {}


class TestSearchSummary:
    def test_no_matches(self):
        msg = search_summary([], "DB_*")
        assert "No" in msg
        assert "DB_*" in msg

    def test_single_match(self):
        msg = search_summary(["DB_HOST"], "DB_*")
        assert "1" in msg
        assert "entry" in msg

    def test_multiple_matches(self):
        msg = search_summary(["DB_HOST", "DB_PORT"], "DB_*")
        assert "2" in msg
        assert "entries" in msg
