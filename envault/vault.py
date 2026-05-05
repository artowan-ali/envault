"""Vault: encrypted storage for environment variables."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import derive_key, encrypt, decrypt


SALT_FILE = "salt.bin"
DATA_FILE = "data.enc"
SALT_SIZE = 16


class Vault:
    """Manages encrypted key-value pairs stored on disk."""

    def __init__(self, path: str, password: str):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self._salt = self._load_or_create_salt()
        self._key = self._derive_key(password)
        self._data: dict = self.load()

    def _load_or_create_salt(self) -> bytes:
        salt_path = self.path / SALT_FILE
        if salt_path.exists():
            return salt_path.read_bytes()
        salt = os.urandom(SALT_SIZE)
        salt_path.write_bytes(salt)
        return salt

    def _derive_key(self, password: str) -> bytes:
        return derive_key(password, self._salt)

    def load(self) -> dict:
        data_path = self.path / DATA_FILE
        if not data_path.exists():
            return {}
        ciphertext = data_path.read_bytes()
        plaintext = decrypt(self._key, ciphertext)
        return json.loads(plaintext)

    def save(self):
        data_path = self.path / DATA_FILE
        plaintext = json.dumps(self._data).encode()
        ciphertext = encrypt(self._key, plaintext)
        data_path.write_bytes(ciphertext)

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def delete(self, key: str):
        self._data.pop(key, None)

    def list_keys(self) -> list:
        return list(self._data.keys())

    def to_dict(self) -> dict:
        return dict(self._data)

    def from_dict(self, data: dict):
        self._data = dict(data)
