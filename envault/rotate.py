"""Key rotation support for envault vaults."""

from pathlib import Path
from envault.vault import Vault
from envault.audit import record_event


def rotate_key(vault_dir: str, old_password: str, new_password: str) -> dict:
    """Re-encrypt all vault entries with a new password.

    Opens the vault with the old password, reads all keys, then
    re-creates the vault salt and re-encrypts everything under the
    new password.  Returns a summary dict with counts.

    Args:
        vault_dir:    Path to the vault directory.
        old_password: Current encryption password.
        new_password: Replacement encryption password.

    Returns:
        {"rotated": <int>, "keys": [<str>, ...]}

    Raises:
        ValueError: If old_password cannot decrypt the vault.
        FileNotFoundError: If vault_dir does not exist.
    """
    vault_path = Path(vault_dir)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault directory not found: {vault_dir}")

    # Load all current secrets with the old password
    old_vault = Vault(vault_dir, old_password)
    keys = old_vault.list_keys()
    secrets = {k: old_vault.get(k) for k in keys}

    # Remove the salt file so the new vault generates a fresh one
    salt_file = vault_path / "salt"
    if salt_file.exists():
        salt_file.unlink()

    # Remove all existing encrypted entry files
    for entry_file in vault_path.glob("*.enc"):
        entry_file.unlink()

    # Re-create the vault under the new password
    new_vault = Vault(vault_dir, new_password)
    for key, value in secrets.items():
        if value is not None:
            new_vault.set(key, value)

    record_event(vault_dir, "rotate_key", {"keys_rotated": len(keys)})

    return {"rotated": len(keys), "keys": keys}
