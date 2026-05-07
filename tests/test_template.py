"""Tests for envault.template."""

import os
import pytest
from envault.template import (
    render_template,
    render_file,
    list_placeholders,
    template_summary,
)


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

class TestRenderTemplate:
    def test_single_placeholder_replaced(self):
        result = render_template("Hello, {{NAME}}!", {"NAME": "Alice"})
        assert result == "Hello, Alice!"

    def test_multiple_placeholders_replaced(self):
        tmpl = "{{GREETING}}, {{NAME}}!"
        result = render_template(tmpl, {"GREETING": "Hi", "NAME": "Bob"})
        assert result == "Hi, Bob!"

    def test_unresolved_placeholder_left_as_is(self):
        result = render_template("{{MISSING}}", {})
        assert result == "{{MISSING}}"

    def test_strict_raises_on_missing(self):
        with pytest.raises(KeyError, match="MISSING"):
            render_template("{{MISSING}}", {}, strict=True)

    def test_extra_spaces_in_placeholder(self):
        result = render_template("{{ DB_HOST }}", {"DB_HOST": "localhost"})
        assert result == "localhost"

    def test_no_placeholders_returns_original(self):
        tmpl = "nothing to replace here"
        assert render_template(tmpl, {"FOO": "bar"}) == tmpl

    def test_duplicate_placeholder_both_replaced(self):
        result = render_template("{{X}} and {{X}}", {"X": "42"})
        assert result == "42 and 42"


# ---------------------------------------------------------------------------
# render_file
# ---------------------------------------------------------------------------

class TestRenderFile:
    def test_reads_and_renders_file(self, tmp_path):
        tmpl = tmp_path / "tmpl.txt"
        tmpl.write_text("PORT={{PORT}}")
        result = render_file(str(tmpl), {"PORT": "8080"})
        assert result == "PORT=8080"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            render_file(str(tmp_path / "nonexistent.txt"), {})

    def test_strict_propagated(self, tmp_path):
        tmpl = tmp_path / "tmpl.txt"
        tmpl.write_text("{{MISSING}}")
        with pytest.raises(KeyError):
            render_file(str(tmpl), {}, strict=True)


# ---------------------------------------------------------------------------
# list_placeholders
# ---------------------------------------------------------------------------

class TestListPlaceholders:
    def test_returns_sorted_unique_names(self):
        tmpl = "{{B}} {{A}} {{B}}"
        assert list_placeholders(tmpl) == ["A", "B"]

    def test_empty_template_returns_empty(self):
        assert list_placeholders("no placeholders") == []


# ---------------------------------------------------------------------------
# template_summary
# ---------------------------------------------------------------------------

class TestTemplateSummary:
    def test_resolved_and_missing(self):
        tmpl = "{{A}} {{B}} {{C}}"
        summary = template_summary(tmpl, {"A": "1", "C": "3"})
        assert summary["resolved"] == ["A", "C"]
        assert summary["missing"] == ["B"]

    def test_all_resolved(self):
        tmpl = "{{X}}"
        summary = template_summary(tmpl, {"X": "ok"})
        assert summary["missing"] == []

    def test_none_resolved(self):
        tmpl = "{{X}}"
        summary = template_summary(tmpl, {})
        assert summary["resolved"] == []
        assert "X" in summary["missing"]
