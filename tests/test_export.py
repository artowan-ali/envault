"""Tests for envault.export module."""

import json
import os
import pytest

from envault.export import (
    export_to_env,
    import_from_env,
    export_to_json,
    import_from_json,
    detect_format,
)


@pytest.fixture
def tmp_env_file(tmp_path):
    return str(tmp_path / ".env")


@pytest.fixture
def tmp_json_file(tmp_path):
    return str(tmp_path / "secrets.json")


class TestEnvFormat:
    def test_export_and_import_roundtrip(self, tmp_env_file):
        secrets = {"DB_HOST": "localhost", "API_KEY": "abc123"}
        export_to_env(secrets, tmp_env_file)
        result = import_from_env(tmp_env_file)
        assert result == secrets

    def test_export_sorts_keys(self, tmp_env_file):
        secrets = {"Z_KEY": "z", "A_KEY": "a"}
        export_to_env(secrets, tmp_env_file)
        with open(tmp_env_file) as f:
            content = f.read()
        assert content.index("A_KEY") < content.index("Z_KEY")

    def test_import_skips_comments(self, tmp_env_file):
        with open(tmp_env_file, "w") as f:
            f.write("# this is a comment\nFOO=bar\n")
        result = import_from_env(tmp_env_file)
        assert result == {"FOO": "bar"}

    def test_import_skips_blank_lines(self, tmp_env_file):
        with open(tmp_env_file, "w") as f:
            f.write("\nFOO=bar\n\n")
        result = import_from_env(tmp_env_file)
        assert result == {"FOO": "bar"}

    def test_value_with_special_chars(self, tmp_env_file):
        secrets = {"MSG": 'say "hello"'}
        export_to_env(secrets, tmp_env_file)
        result = import_from_env(tmp_env_file)
        assert result == secrets

    def test_value_with_newline(self, tmp_env_file):
        secrets = {"MULTILINE": "line1\nline2"}
        export_to_env(secrets, tmp_env_file)
        result = import_from_env(tmp_env_file)
        assert result == secrets


class TestJsonFormat:
    def test_export_and_import_roundtrip(self, tmp_json_file):
        secrets = {"DB_HOST": "localhost", "API_KEY": "abc123"}
        export_to_json(secrets, tmp_json_file)
        result = import_from_json(tmp_json_file)
        assert result == secrets

    def test_export_is_valid_json(self, tmp_json_file):
        secrets = {"KEY": "value"}
        export_to_json(secrets, tmp_json_file)
        with open(tmp_json_file) as f:
            data = json.load(f)
        assert data == secrets

    def test_import_raises_on_non_dict(self, tmp_json_file):
        with open(tmp_json_file, "w") as f:
            json.dump(["not", "a", "dict"], f)
        with pytest.raises(ValueError, match="top-level object"):
            import_from_json(tmp_json_file)


class TestDetectFormat:
    def test_detects_json(self):
        assert detect_format("secrets.json") == "json"

    def test_detects_env(self):
        assert detect_format(".env") == "env"
        assert detect_format("local.env") == "env"

    def test_unknown_extension_returns_none(self):
        assert detect_format("secrets.yaml") is None

    def test_no_extension_returns_env(self):
        assert detect_format("envfile") == "env"
