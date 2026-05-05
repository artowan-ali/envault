"""Vault module for managing encrypted environment variables."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import derive_key, encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"
DEFAULT_SALT_FILE = ".envault.salt"


class Vault:
    """Manages encrypted environment variables stored in a local vault file."""

    def __init__(self, vault_path: str = DEFAULT_VAULT_FILE, salt_path: str = DEFAULT_SALT_FILE):
        self.vault_path = Path(vault_path)
        self.salt_path = Path(salt_path)
        self._data: Dict[str, str] = {}

    def _load_or_create_salt(self) -> bytes:
        """Load existing salt or generate and persist a new one."""
        if self.salt_path.exists():
            return self.salt_path.read_bytes()
        salt = os.urandom(16)
        self.salt_path.write_bytes(salt)
        return salt

    def _derive_key(self, password: str) -> bytes:
        salt = self._load_or_create_salt()
        return derive_key(password, salt)

    def load(self, password: str) -> None:
        """Load and decrypt vault contents from disk."""
        if not self.vault_path.exists():
            self._data = {}
            return
        key = self._derive_key(password)
        ciphertext = self.vault_path.read_bytes()
        plaintext = decrypt(key, ciphertext)
        self._data = json.loads(plaintext)

    def save(self, password: str) -> None:
        """Encrypt and persist vault contents to disk."""
        key = self._derive_key(password)
        plaintext = json.dumps(self._data).encode()
        ciphertext = encrypt(key, plaintext)
        self.vault_path.write_bytes(ciphertext)

    def set(self, key: str, value: str) -> None:
        """Set an environment variable in the vault."""
        self._data[key] = value

    def get(self, key: str) -> Optional[str]:
        """Retrieve an environment variable from the vault."""
        return self._data.get(key)

    def delete(self, key: str) -> bool:
        """Remove a variable from the vault. Returns True if it existed."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    def list_keys(self) -> list:
        """Return all variable names stored in the vault."""
        return sorted(self._data.keys())

    def export(self) -> Dict[str, str]:
        """Return a copy of all key-value pairs."""
        return dict(self._data)
