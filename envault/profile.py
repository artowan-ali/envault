"""Profile support: named environment profiles (e.g. dev, staging, prod)."""

import json
from pathlib import Path

_PROFILES_FILE = "profiles.json"


def _load_profiles(vault_dir: str) -> dict:
    path = Path(vault_dir) / _PROFILES_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_profiles(vault_dir: str, profiles: dict) -> None:
    path = Path(vault_dir) / _PROFILES_FILE
    with open(path, "w") as f:
        json.dump(profiles, f, indent=2)


def set_profile_key(vault_dir: str, profile: str, key: str, value: str) -> None:
    """Assign a key-value pair to a named profile."""
    profiles = _load_profiles(vault_dir)
    profiles.setdefault(profile, {})[key] = value
    _save_profiles(vault_dir, profiles)


def get_profile_key(vault_dir: str, profile: str, key: str) -> str | None:
    """Retrieve a key's value from a named profile."""
    profiles = _load_profiles(vault_dir)
    return profiles.get(profile, {}).get(key)


def delete_profile_key(vault_dir: str, profile: str, key: str) -> bool:
    """Remove a key from a profile. Returns True if the key existed."""
    profiles = _load_profiles(vault_dir)
    if profile in profiles and key in profiles[profile]:
        del profiles[profile][key]
        if not profiles[profile]:
            del profiles[profile]
        _save_profiles(vault_dir, profiles)
        return True
    return False


def list_profiles(vault_dir: str) -> list[str]:
    """Return a sorted list of existing profile names."""
    return sorted(_load_profiles(vault_dir).keys())


def get_profile(vault_dir: str, profile: str) -> dict:
    """Return all key-value pairs for a profile."""
    return dict(_load_profiles(vault_dir).get(profile, {}))


def delete_profile(vault_dir: str, profile: str) -> bool:
    """Delete an entire profile. Returns True if it existed."""
    profiles = _load_profiles(vault_dir)
    if profile in profiles:
        del profiles[profile]
        _save_profiles(vault_dir, profiles)
        return True
    return False


def profile_summary(vault_dir: str) -> str:
    profiles = _load_profiles(vault_dir)
    if not profiles:
        return "No profiles defined."
    lines = []
    for name in sorted(profiles):
        count = len(profiles[name])
        lines.append(f"  {name}: {count} key(s)")
    return "Profiles:\n" + "\n".join(lines)
