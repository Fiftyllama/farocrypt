"""
Faro Cipher Utilities
====================

Utility functions for the Faro Cipher package.
"""

import numpy as np
from typing import Tuple

try:
    from numba import njit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

@njit
def pad_to_power_of_2(bits: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Pad bit array to the next power of 2 length.
    
    Args:
        bits: Input bit array
        
    Returns:
        Tuple of (padded_bits, original_length)
    """
    original_length = len(bits)
    
    # Find next power of 2
    if original_length <= 1:
        target_length = 1
    else:
        # Calculate next power of 2
        target_length = 1
        while target_length < original_length:
            target_length *= 2
    
    # Pad with zeros using array creation - ensure consistent uint8 type
    if target_length > original_length:
        padded_bits = np.zeros(target_length, dtype=np.uint8)
        # Ensure input bits are also uint8
        bits_uint8 = bits.astype(np.uint8)
        padded_bits[:original_length] = bits_uint8
    else:
        padded_bits = bits.astype(np.uint8)
    
    return padded_bits, original_length

def generate_key_fingerprint(key: bytes) -> str:
    """Generate a short fingerprint for a key"""
    import hashlib
    return hashlib.md5(key).hexdigest()[:16]

def verify_key_compatibility(key: bytes, fingerprint: str) -> bool:
    """Verify if a key matches a fingerprint"""
    return generate_key_fingerprint(key) == fingerprint 