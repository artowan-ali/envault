"""Tests for envault.crypto encryption/decryption utilities."""

import base64
import pytest

from envault.crypto import encrypt, decrypt, derive_key


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "MY_SECRET=hello_world"


class TestDeriveKey:
    def test_returns_32_bytes(self):
        key = derive_key(PASSPHRASE, b"saltsaltsaltsalt")
        assert len(key) == 32

    def test_deterministic(self):
        salt = b"fixed_salt_12345"
        assert derive_key(PASSPHRASE, salt) == derive_key(PASSPHRASE, salt)

    def test_different_salts_produce_different_keys(self):
        assert derive_key(PASSPHRASE, b"salt1salt1salt10") != derive_key(PASSPHRASE, b"salt2salt2salt20")


class TestEncryptDecrypt:
    def test_roundtrip(self):
        token = encrypt(PLAINTEXT, PASSPHRASE)
        assert decrypt(token, PASSPHRASE) == PLAINTEXT

    def test_encrypt_returns_string(self):
        token = encrypt(PLAINTEXT, PASSPHRASE)
        assert isinstance(token, str)

    def test_encrypt_is_non_deterministic(self):
        """Each call should produce a different ciphertext due to random salt/nonce."""
        token1 = encrypt(PLAINTEXT, PASSPHRASE)
        token2 = encrypt(PLAINTEXT, PASSPHRASE)
        assert token1 != token2

    def test_wrong_passphrase_raises(self):
        token = encrypt(PLAINTEXT, PASSPHRASE)
        with pytest.raises(ValueError, match="Decryption failed"):
            decrypt(token, "wrong-passphrase")

    def test_tampered_ciphertext_raises(self):
        token = encrypt(PLAINTEXT, PASSPHRASE)
        raw = base64.b64decode(token)
        # Flip a byte in the ciphertext area
        tampered = bytearray(raw)
        tampered[-1] ^= 0xFF
        bad_token = base64.b64encode(bytes(tampered)).decode("ascii")
        with pytest.raises(ValueError):
            decrypt(bad_token, PASSPHRASE)

    def test_invalid_base64_raises(self):
        with pytest.raises(ValueError, match="Invalid base64"):
            decrypt("!!!not-base64!!!", PASSPHRASE)

    def test_payload_too_short_raises(self):
        short = base64.b64encode(b"tooshort").decode("ascii")
        with pytest.raises(ValueError, match="Payload too short"):
            decrypt(short, PASSPHRASE)

    def test_empty_string_roundtrip(self):
        token = encrypt("", PASSPHRASE)
        assert decrypt(token, PASSPHRASE) == ""

    def test_unicode_roundtrip(self):
        unicode_text = "SECRET=caf\u00e9_\u4e2d\u6587"
        token = encrypt(unicode_text, PASSPHRASE)
        assert decrypt(token, PASSPHRASE) == unicode_text
