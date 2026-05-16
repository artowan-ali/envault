"""Policy enforcement for vault keys (e.g. required keys, value patterns)."""

import json
import re
from pathlib import Path


def _policy_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "policy.json"


def _load_policies(vault_dir: str) -> dict:
    path = _policy_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_policies(vault_dir: str, policies: dict) -> None:
    with open(_policy_path(vault_dir), "w") as f:
        json.dump(policies, f, indent=2)


def set_policy(vault_dir: str, key: str, required: bool = False, pattern: str = None) -> None:
    """Set a policy rule for a key."""
    policies = _load_policies(vault_dir)
    policies[key] = {
        "required": required,
        "pattern": pattern,
    }
    _save_policies(vault_dir, policies)


def remove_policy(vault_dir: str, key: str) -> bool:
    """Remove a policy rule. Returns True if it existed."""
    policies = _load_policies(vault_dir)
    if key in policies:
        del policies[key]
        _save_policies(vault_dir, policies)
        return True
    return False


def get_policy(vault_dir: str, key: str) -> dict | None:
    """Return the policy for a key, or None."""
    return _load_policies(vault_dir).get(key)


def list_policies(vault_dir: str) -> dict:
    """Return all policies."""
    return _load_policies(vault_dir)


def validate(vault_dir: str, store: dict) -> list[dict]:
    """Validate store against policies. Returns list of violation dicts."""
    policies = _load_policies(vault_dir)
    violations = []
    for key, rule in policies.items():
        if rule.get("required") and key not in store:
            violations.append({"key": key, "reason": "required key missing"})
            continue
        if key in store and rule.get("pattern"):
            value = store[key]
            if not re.fullmatch(rule["pattern"], value):
                violations.append({
                    "key": key,
                    "reason": f"value does not match pattern '{rule['pattern']}'",
                })
    return violations
