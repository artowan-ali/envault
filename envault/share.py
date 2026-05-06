"""Team sharing support via git-compatible encrypted diffs."""

import json
import os
from typing import Optional

from envault.diff import generate_diff, serialize_diff, deserialize_diff, apply_diff
from envault.vault import Vault


def export_share_patch(vault: Vault, recipient_password: str, base_vault: Optional[Vault] = None) -> str:
    """Generate an encrypted share patch from vault state.

    If base_vault is provided, only the diff from base_vault to vault is included.
    Otherwise, all current keys are treated as additions.
    """
    current_data = {k: vault.get(k) for k in vault.list_keys()}

    if base_vault is not None:
        base_data = {k: base_vault.get(k) for k in base_vault.list_keys()}
    else:
        base_data = {}

    diff = generate_diff(base_data, current_data)
    serialized = serialize_diff(diff)

    tmp_vault_dir = os.path.join(vault.vault_dir, ".share_tmp")
    os.makedirs(tmp_vault_dir, exist_ok=True)
    try:
        share_vault = Vault(tmp_vault_dir, recipient_password)
        share_vault.set("_diff", serialized)
        patch_path = os.path.join(vault.vault_dir, "share.patch")
        with open(patch_path, "w") as f:
            json.dump({
                "salt": share_vault._load_or_create_salt().hex(),
                "diff": share_vault.get("_diff"),
            }, f, indent=2)
        return patch_path
    finally:
        import shutil
        shutil.rmtree(tmp_vault_dir, ignore_errors=True)


def import_share_patch(patch_path: str, recipient_password: str, target_vault: Vault) -> dict:
    """Apply an encrypted share patch to a target vault.

    Returns a summary dict with counts of added/modified/removed keys.
    """
    with open(patch_path, "r") as f:
        payload = json.load(f)

    tmp_vault_dir = os.path.join(target_vault.vault_dir, ".import_tmp")
    os.makedirs(tmp_vault_dir, exist_ok=True)
    try:
        import_vault = Vault(tmp_vault_dir, recipient_password)
        serialized = payload["diff"]
        diff = deserialize_diff(serialized)

        current_data = {k: target_vault.get(k) for k in target_vault.list_keys()}
        updated_data = apply_diff(current_data, diff)

        added = [k for k in updated_data if k not in current_data]
        modified = [k for k in updated_data if k in current_data and updated_data[k] != current_data[k]]
        removed = [k for k in current_data if k not in updated_data]

        for key, value in updated_data.items():
            target_vault.set(key, value)
        for key in removed:
            target_vault.delete(key)

        return {"added": added, "modified": modified, "removed": removed}
    finally:
        import shutil
        shutil.rmtree(tmp_vault_dir, ignore_errors=True)
