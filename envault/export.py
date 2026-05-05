"""Export and import vault contents to/from various formats."""

import json
import os
from typing import Dict, Optional


def export_to_env(secrets: Dict[str, str], path: str) -> None:
    """Export secrets to a .env file format."""
    lines = []
    for key, value in sorted(secrets.items()):
        # Escape newlines and wrap in quotes if value contains special chars
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        lines.append(f'{key}="{escaped}"')
    with open(path, "w") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


def import_from_env(path: str) -> Dict[str, str]:
    """Import secrets from a .env file format."""
    secrets = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            key = key.strip()
            raw_value = raw_value.strip()
            # Strip surrounding quotes
            if len(raw_value) >= 2 and raw_value[0] == '"' and raw_value[-1] == '"':
                raw_value = raw_value[1:-1]
            # Unescape
            value = raw_value.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
            secrets[key] = value
    return secrets


def export_to_json(secrets: Dict[str, str], path: str) -> None:
    """Export secrets to a JSON file."""
    with open(path, "w") as f:
        json.dump(secrets, f, indent=2, sort_keys=True)
        f.write("\n")


def import_from_json(path: str) -> Dict[str, str]:
    """Import secrets from a JSON file."""
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON file must contain a top-level object")
    return {str(k): str(v) for k, v in data.items()}


def detect_format(path: str) -> Optional[str]:
    """Detect file format from extension."""
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext == ".json":
        return "json"
    if ext in (".env", ""):
        return "env"
    return None
