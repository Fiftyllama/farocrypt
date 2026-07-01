"""
Faro Cipher Transform Functions
================================
Seven self-inverse byte-level transforms. "Self-inverse" means applying a transform
twice with the same key returns the original data, so encryption and decryption
use the exact same transform function.

Each transform operates on full bytes (XOR 0xFF to flip all 8 bits) rather than
individual bits, giving an 8x memory and speed improvement over the bit-level approach.

Every function operates on the last axis, so it accepts either a single chunk
(1-D array) or a batch of chunks with identical parameters (2-D array, shape
(n_chunks, chunk_size)) — the position-dependent masks only depend on the
column index, which lets a whole round's chunks be transformed in one call
instead of looping chunk by chunk in Python.
"""

import numpy as np

# Maps name -> callable for use by the round structure.
AVAILABLE_TRANSFORMS: dict


def enhanced_xor(data: np.ndarray, key: int) -> np.ndarray:
    """Flip bytes at positions where (key + i*7) % 256 is divisible by 3."""
    result = data.copy()
    idx = np.arange(data.shape[-1])
    mask = (key + idx * 7) % 256 % 3 == 0
    result[..., mask] ^= 0xFF
    return result


def fibonacci(data: np.ndarray, key: int) -> np.ndarray:
    """Flip bytes at positions determined by a Fibonacci-like sequence seeded by key."""
    result = data.copy()
    n = data.shape[-1]
    fib_a, fib_b = key % 100, (key // 100) % 100
    flip = np.zeros(n, dtype=bool)
    for i in range(n):
        if fib_a % 4 == 0:
            flip[i] = True
        fib_a, fib_b = fib_b, (fib_a + fib_b) % 1000
    result[..., flip] ^= 0xFF
    return result


def avalanche_cascade(data: np.ndarray, key: int) -> np.ndarray:
    """Flip bytes that satisfy any of three overlapping key-dependent patterns."""
    result = data.copy()
    idx = np.arange(data.shape[-1])
    p1 = (key + idx * 7)  % 256
    p2 = (key * 3 + idx * 13) % 256
    p3 = (key ^ (idx * 17)) % 256
    mask = (p1 % 8 == 0) | (p2 % 7 == 1) | (p3 % 9 == 3)
    result[..., mask] ^= 0xFF
    return result


def prime_sieve(data: np.ndarray, key: int) -> np.ndarray:
    """Flip bytes at positions (offset by key) that pass a simple primality test."""
    result = data.copy()
    n = data.shape[-1]
    base = 2 + (key % 97)
    pos = np.arange(n, dtype=np.int64) + base
    # Same trial-division cap as the original: divisors 2..min(floor(sqrt(pos)), 19).
    upper = np.minimum(np.floor(np.sqrt(pos.astype(np.float64))).astype(np.int64) + 1, 20)
    composite = np.zeros(n, dtype=bool)
    for j in range(2, 20):
        composite |= (j < upper) & (pos % j == 0)
    is_prime = (pos >= 2) & ~composite
    result[..., is_prime] ^= 0xFF
    return result


def invert(data: np.ndarray, key: int) -> np.ndarray:
    """Flip bytes at every third position offset by key."""
    result = data.copy()
    idx = np.arange(data.shape[-1])
    result[..., (idx + key) % 3 == 0] ^= 0xFF
    return result


def swap_pairs(data: np.ndarray, key: int) -> np.ndarray:
    """Swap adjacent byte pairs at positions where (i + key) % 4 == 0."""
    result = data.copy()
    n = data.shape[-1]
    pair_starts = np.arange(0, n - 1, 2)
    swap_at = pair_starts[(pair_starts + key) % 4 == 0]
    tmp = result[..., swap_at].copy()
    result[..., swap_at] = result[..., swap_at + 1]
    result[..., swap_at + 1] = tmp
    return result


def bit_flip(data: np.ndarray, key: int) -> np.ndarray:
    """Flip bytes at positions where (i * key) % 7 == 0."""
    result = data.copy()
    idx = np.arange(data.shape[-1])
    result[..., (idx * key) % 7 == 0] ^= 0xFF
    return result


AVAILABLE_TRANSFORMS = {
    'enhanced_xor':    enhanced_xor,
    'fibonacci':       fibonacci,
    'avalanche_cascade': avalanche_cascade,
    'prime_sieve':     prime_sieve,
    'invert':          invert,
    'swap_pairs':      swap_pairs,
    'bit_flip':        bit_flip,
}
