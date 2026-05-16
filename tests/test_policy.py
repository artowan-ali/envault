"""Tests for envault.policy."""

import pytest
from envault.policy import (
    set_policy, remove_policy, get_policy, list_policies, validate
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


class TestSetAndGetPolicy:
    def test_set_and_get(self, vault_dir):
        set_policy(vault_dir, "API_KEY", required=True, pattern=r"[A-Z0-9]+")
        policy = get_policy(vault_dir, "API_KEY")
        assert policy["required"] is True
        assert policy["pattern"] == r"[A-Z0-9]+"

    def test_missing_key_returns_none(self, vault_dir):
        assert get_policy(vault_dir, "MISSING") is None

    def test_overwrite_existing_policy(self, vault_dir):
        set_policy(vault_dir, "KEY", required=True)
        set_policy(vault_dir, "KEY", required=False, pattern=r"\d+")
        policy = get_policy(vault_dir, "KEY")
        assert policy["required"] is False
        assert policy["pattern"] == r"\d+"

    def test_defaults_are_falsy(self, vault_dir):
        set_policy(vault_dir, "SIMPLE")
        policy = get_policy(vault_dir, "SIMPLE")
        assert policy["required"] is False
        assert policy["pattern"] is None


class TestRemovePolicy:
    def test_remove_existing_returns_true(self, vault_dir):
        set_policy(vault_dir, "KEY", required=True)
        assert remove_policy(vault_dir, "KEY") is True
        assert get_policy(vault_dir, "KEY") is None

    def test_remove_missing_returns_false(self, vault_dir):
        assert remove_policy(vault_dir, "NONEXISTENT") is False


class TestListPolicies:
    def test_empty_when_no_policies(self, vault_dir):
        assert list_policies(vault_dir) == {}

    def test_returns_all_policies(self, vault_dir):
        set_policy(vault_dir, "A", required=True)
        set_policy(vault_dir, "B", pattern=r"\w+")
        policies = list_policies(vault_dir)
        assert "A" in policies
        assert "B" in policies


class TestValidate:
    def test_no_violations_when_store_matches(self, vault_dir):
        set_policy(vault_dir, "DB_URL", required=True, pattern=r"postgres://.*")
        store = {"DB_URL": "postgres://localhost/db"}
        assert validate(vault_dir, store) == []

    def test_missing_required_key(self, vault_dir):
        set_policy(vault_dir, "SECRET", required=True)
        violations = validate(vault_dir, {})
        assert len(violations) == 1
        assert violations[0]["key"] == "SECRET"
        assert "required" in violations[0]["reason"]

    def test_pattern_violation(self, vault_dir):
        set_policy(vault_dir, "PORT", pattern=r"\d+")
        violations = validate(vault_dir, {"PORT": "not-a-number"})
        assert len(violations) == 1
        assert "pattern" in violations[0]["reason"]

    def test_no_policies_no_violations(self, vault_dir):
        assert validate(vault_dir, {"ANY": "value"}) == []

    def test_optional_missing_key_no_violation(self, vault_dir):
        set_policy(vault_dir, "OPTIONAL_KEY", required=False)
        assert validate(vault_dir, {}) == []
