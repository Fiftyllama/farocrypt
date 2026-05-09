"""
Faro Cipher Shuffle Functions
==============================
Byte-level shuffle and inverse-shuffle implementations for all five shuffle types
(none, in, out, milk, cut) with four variants each. Operates directly on bytes,
avoiding bit-expansion for an 8x memory and speed improvement over bit-level code.
"""

import numpy as np

# All shuffle types and their valid variant indices.
RELIABLE_SHUFFLE_VARIANTS = {
    'none': [0, 1, 2, 3],
    'in':   [0, 1, 2, 3],
    'out':  [0, 1, 2, 3],
    'milk': [0, 1, 2, 3],
    'cut':  [0, 1, 2, 3],
}


def shuffle(data: np.ndarray, shuffle_type: str, steps: int, variant: int) -> np.ndarray:
    """Apply a faro shuffle `steps` times to a byte array."""
    result = data.copy()
    for _ in range(steps):
        result = _shuffle_step(result, shuffle_type, variant % 4)
    return result


def inverse_shuffle(data: np.ndarray, shuffle_type: str, steps: int, variant: int) -> np.ndarray:
    """Reverse a shuffle applied with the given parameters."""
    result = data.copy()
    for _ in range(steps):
        result = _inverse_shuffle_step(result, shuffle_type, variant % 4)
    return result


# ---------------------------------------------------------------------------
# Single-step forward shuffles
# ---------------------------------------------------------------------------

def _shuffle_step(data: np.ndarray, shuffle_type: str, variant: int) -> np.ndarray:
    n = len(data)
    if n <= 1 or shuffle_type == 'none':
        return data.copy()

    result = np.empty_like(data)
    mid = n // 2

    if shuffle_type == 'in':
        # Interleave two halves: [a0..ak, b0..bk] -> [a0,b0,a1,b1,...]
        first, second = data[:n - mid], data[n - mid:]
        if variant == 0:
            result[0::2] = first;  result[1::2] = second
        elif variant == 1:
            result[0::2] = second; result[1::2] = first
        elif variant == 2:
            result[1::2] = first;  result[0::2] = second
        else:  # variant == 3
            result[1::2] = second; result[0::2] = first

    elif shuffle_type == 'out':
        # De-interleave: [a0,b0,a1,b1,...] -> [a0,a1,..., b0,b1,...]
        if variant == 0:
            result[:n - mid] = data[0::2]; result[n - mid:] = data[1::2]
        elif variant == 1:
            result[:mid] = data[1::2][:mid]; result[mid:] = data[0::2][:n - mid]
        elif variant == 2:
            result[1::2] = data[:mid]; result[0::2] = data[mid:]
        else:  # variant == 3
            result[0::2] = data[mid:]; result[1::2] = data[:mid]

    elif shuffle_type == 'milk':
        # Alternate taking bytes from the top and bottom halves.
        idx = np.arange(n)
        even = idx % 2 == 0
        if variant == 0:
            result[even]  = data[idx[even] // 2]
            result[~even] = data[n - 1 - idx[~even] // 2]
        elif variant == 1:
            result[even]  = data[n - 1 - idx[even] // 2]
            result[~even] = data[idx[~even] // 2]
        elif variant == 2:
            shifted = (idx + 1) % 2 == 0
            result[shifted]  = data[idx[shifted] // 2]
            result[~shifted] = data[n - 1 - idx[~shifted] // 2]
        else:  # variant == 3
            shifted = (idx + 1) % 2 == 0
            result[shifted]  = data[n - 1 - idx[shifted] // 2]
            result[~shifted] = data[idx[~shifted] // 2]

    elif shuffle_type == 'cut':
        # Move two bytes from one position to another.
        cut = 2 if n > 2 else 1
        half = n // 2
        if variant == 0:  # cut from top, insert at middle
            result[:half]             = data[cut:cut + half]
            result[half:half + cut]   = data[:cut]
            result[half + cut:]       = data[cut + half:]
        elif variant == 1:  # cut from bottom, insert at middle
            result[:half - cut]       = data[:half - cut]
            result[half - cut:half]   = data[n - cut:]
            result[half:]             = data[half - cut:n - cut]
        elif variant == 2:  # cut from middle, move to top
            result[:cut]              = data[half:half + cut]
            result[cut:cut + half]    = data[:half]
            result[cut + half:]       = data[half + cut:]
        else:  # variant == 3 — cut from middle, move to bottom
            result[:half]             = data[:half]
            result[half:n - cut]      = data[half + cut:]
            result[n - cut:]          = data[half:half + cut]

    return result


# ---------------------------------------------------------------------------
# Single-step inverse shuffles
# ---------------------------------------------------------------------------

def _inverse_shuffle_step(data: np.ndarray, shuffle_type: str, variant: int) -> np.ndarray:
    n = len(data)
    if n <= 1 or shuffle_type == 'none':
        return data.copy()

    result = np.empty_like(data)
    mid = n // 2

    if shuffle_type == 'in':
        first_len = n - mid
        if variant == 0:
            result[:first_len] = data[0::2]; result[first_len:] = data[1::2]
        elif variant == 1:
            result[:mid] = data[1::2]; result[mid:] = data[0::2]
        elif variant == 2:
            result[:mid] = data[1::2]; result[mid:] = data[0::2]
        else:  # variant == 3
            result[:first_len] = data[0::2]; result[first_len:] = data[1::2]

    elif shuffle_type == 'out':
        first_len = n - mid
        if variant == 0:
            result[0::2] = data[:first_len]; result[1::2] = data[first_len:]
        elif variant == 1:
            result[1::2] = data[:mid]; result[0::2] = data[mid:]
        elif variant == 2:
            result[:mid] = data[1::2]; result[mid:] = data[0::2]
        else:  # variant == 3
            result[mid:] = data[0::2]; result[:mid] = data[1::2]

    elif shuffle_type == 'milk':
        idx = np.arange(n)
        even = idx % 2 == 0
        if variant == 0:
            result[idx[even] // 2]          = data[even]
            result[n - 1 - idx[~even] // 2] = data[~even]
        elif variant == 1:
            result[n - 1 - idx[even] // 2]  = data[even]
            result[idx[~even] // 2]          = data[~even]
        elif variant == 2:
            shifted = (idx + 1) % 2 == 0
            result[idx[shifted] // 2]           = data[shifted]
            result[n - 1 - idx[~shifted] // 2]  = data[~shifted]
        else:  # variant == 3
            shifted = (idx + 1) % 2 == 0
            result[n - 1 - idx[shifted] // 2]   = data[shifted]
            result[idx[~shifted] // 2]           = data[~shifted]

    elif shuffle_type == 'cut':
        cut = 2 if n > 2 else 1
        half = n // 2
        if variant == 0:
            result[:cut]           = data[half:half + cut]
            result[cut:cut + half] = data[:half]
            result[cut + half:]    = data[half + cut:]
        elif variant == 1:
            result[:half - cut]    = data[:half - cut]
            result[n - cut:]       = data[half - cut:half]
            result[half - cut:n - cut] = data[half:]
        elif variant == 2:
            result[:half]          = data[cut:cut + half]
            result[half:half + cut] = data[:cut]
            result[half + cut:]    = data[cut + half:]
        else:  # variant == 3
            result[:half]          = data[:half]
            result[half:half + cut] = data[n - cut:]
            result[half + cut:]    = data[half:n - cut]

    return result
