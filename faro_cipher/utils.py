"""
Faro Cipher Utilities
======================
Key fingerprinting helpers used by FaroCipher.
"""

import hashlib


def generate_key_fingerprint(key: bytes) -> str:
    """Return a 16-character hex fingerprint of a key (for compatibility checking)."""
    return hashlib.md5(key).hexdigest()[:16]


def verify_key_compatibility(key: bytes, fingerprint: str) -> bool:
    """Return True if key produces the given fingerprint."""
    return generate_key_fingerprint(key) == fingerprint
