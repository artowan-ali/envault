"""Core Vault class for envault — manages encrypted key-value storage."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from envault.crypto import derive_key, encrypt, decrypt

SALT_FILE = "salt.bin"
VAULT_FILE = "vault.json"


class Vault:
    def __init__(self, vault_dir: Path, password: str) -> None:
        self._vault_dir = Path(vault_dir)
        self._vault_dir.mkdir(parents=True, exist_ok=True)
        self._salt = self._load_or_create_salt()
        self._key = self._derive_key(password)
        self._store: Dict[str, str] = self._load_store()

    def _load_or_create_salt(self) -> bytes:
        path = self._vault_dir / SALT_FILE
        if path.exists():
            return path.read_bytes()
        salt = os.urandom(16)
        path.write_bytes(salt)
        return salt

    def _derive_key(self, password: str) -> bytes:
        return derive_key(password, self._salt)

    def _load_store(self) -> Dict[str, str]:
        path = self._vault_dir / VAULT_FILE
        if not path.exists():
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def _save_store(self) -> None:
        path = self._vault_dir / VAULT_FILE
        with open(path, "w") as f:
            json.dump(self._store, f, indent=2)

    def _encrypt_value(self, value: str) -> str:
        return encrypt(self._key, value)

    def _decrypt_value(self, token: str) -> str:
        return decrypt(self._key, token)

    def load(self) -> Dict[str, str]:
        """Return all decrypted key-value pairs."""
        return {k: self._decrypt_value(v) for k, v in self._store.items()}

    def set(self, key: str, value: str) -> None:
        self._store[key] = self._encrypt_value(value)
        self._save_store()

    def get(self, key: str) -> Optional[str]:
        if key not in self._store:
            return None
        return self._decrypt_value(self._store[key])

    def delete(self, key: str) -> bool:
        if key not in self._store:
            return False
        del self._store[key]
        self._save_store()
        return True

    def keys(self) -> List[str]:
        return list(self._store.keys())

    def has(self, key: str) -> bool:
        return key in self._store
