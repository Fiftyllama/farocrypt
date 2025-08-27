"""
Faro Cipher JIT Optimized Functions
===================================

High-performance JIT-compiled functions using Numba for critical cipher operations.
"""

import numpy as np
from typing import Tuple

try:
    from numba import njit, types
    from numba.typed import Dict as NumbaDict
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from .utils import pad_to_power_of_2
from .shuffles import faro_shuffle, inverse_faro_shuffle
from .transforms import AVAILABLE_TRANSFORMS

@njit
def bytes_to_bits_jit(data: np.ndarray) -> np.ndarray:
    """
    JIT-optimized conversion from bytes to bits
    
    Args:
        data: Input byte array (numpy uint8)
        
    Returns:
        Bit array (numpy uint8)
    """
    n_bytes = len(data)
    bits = np.zeros(n_bytes * 8, dtype=np.uint8)
    
    for i in range(n_bytes):
        byte_val = data[i]
        for j in range(8):
            # Extract bit j from byte (MSB first, like np.unpackbits)
            bit_pos = i * 8 + j
            bits[bit_pos] = (byte_val >> (7 - j)) & 1
    
    return bits

@njit
def bits_to_bytes_jit(bits: np.ndarray) -> np.ndarray:
    """
    JIT-optimized conversion from bits to bytes
    
    Args:
        bits: Input bit array (numpy uint8)
        
    Returns:
        Byte array (numpy uint8)
    """
    n_bits = len(bits)
    
    # Ensure bits array length is multiple of 8
    remainder = n_bits % 8
    if remainder != 0:
        # Pad with zeros to make it multiple of 8
        padding = 8 - remainder
        padded_bits = np.zeros(n_bits + padding, dtype=np.uint8)
        padded_bits[:n_bits] = bits
        bits = padded_bits
        n_bits = len(bits)
    
    n_bytes = n_bits // 8
    bytes_array = np.zeros(n_bytes, dtype=np.uint8)
    
    for i in range(n_bytes):
        byte_val = 0
        for j in range(8):
            bit_pos = i * 8 + j
            # Reconstruct byte (MSB first, like np.packbits)
            if bits[bit_pos]:
                byte_val |= (1 << (7 - j))
        bytes_array[i] = byte_val
    
    return bytes_array

@njit
def pad_to_power_of_2_jit(bits: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    JIT-optimized padding to power of 2
    
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
        target_length = 1
        while target_length < original_length:
            target_length *= 2
    
    # Pad with zeros
    if target_length > original_length:
        padded_bits = np.zeros(target_length, dtype=np.uint8)
        padded_bits[:original_length] = bits
    else:
        padded_bits = bits.copy()
    
    return padded_bits, original_length

@njit
def apply_transform_jit(bits: np.ndarray, transform_type: int, key: int) -> np.ndarray:
    """
    JIT-optimized transform application
    
    Args:
        bits: Input bit array
        transform_type: Transform type (0-6 for different transforms)
        key: Transform key
        
    Returns:
        Transformed bit array
    """
    result = bits.copy()
    n = len(result)
    
    if transform_type == 0:  # enhanced_xor
        for i in range(n):
            pattern = (key + i * 7) % 256
            if pattern % 3 == 0:
                result[i] = 1 - result[i]
                
    elif transform_type == 1:  # fibonacci
        if n >= 2:
            fib_a, fib_b = key % 100, (key // 100) % 100
            for i in range(n):
                if fib_a % 4 == 0:
                    result[i] = 1 - result[i]
                fib_a, fib_b = fib_b, (fib_a + fib_b) % 1000
                
    elif transform_type == 2:  # avalanche_cascade
        for i in range(n):
            pattern1 = (key + i * 7) % 256
            pattern2 = (key * 3 + i * 13) % 256
            pattern3 = (key ^ (i * 17)) % 256
            if (pattern1 % 8 == 0) or (pattern2 % 7 == 1) or (pattern3 % 9 == 3):
                result[i] = 1 - result[i]
                
    elif transform_type == 3:  # prime_sieve
        base_prime = 2 + (key % 97)
        for i in range(n):
            pos = i + base_prime
            is_prime_pos = True
            if pos < 2:
                is_prime_pos = False
            else:
                for j in range(2, min(int(pos**0.5) + 1, 20)):
                    if pos % j == 0:
                        is_prime_pos = False
                        break
            if is_prime_pos:
                result[i] = 1 - result[i]
                
    elif transform_type == 4:  # invert
        for i in range(n):
            if (i + key) % 3 == 0:
                result[i] = 1 - result[i]
                
    elif transform_type == 5:  # swap_pairs
        for i in range(0, n - 1, 2):
            if (i + key) % 4 == 0:
                result[i], result[i + 1] = result[i + 1], result[i]
                
    elif transform_type == 6:  # bit_flip
        for i in range(n):
            if (i * key) % 7 == 0:
                result[i] = 1 - result[i]
    
    return result

@njit
def process_single_chunk_jit(chunk_bytes: np.ndarray, 
                           shuffle_type: int,
                           shuffle_steps: int, 
                           shuffle_variant: int,
                           transform_type: int,
                           transform_key: int,
                           encrypt: bool) -> np.ndarray:
    """
    JIT-optimized single chunk processing
    
    Args:
        chunk_bytes: Input chunk as byte array
        shuffle_type: Shuffle type (0=none, 1=in, 2=out, 3=milk, 4=cut)
        shuffle_steps: Number of shuffle steps
        shuffle_variant: Shuffle variant
        transform_type: Transform type (0-6)
        transform_key: Transform key
        encrypt: True for encryption, False for decryption
        
    Returns:
        Processed chunk as byte array
    """
    if len(chunk_bytes) == 0:
        return chunk_bytes
    
    # Convert to bits
    bits = bytes_to_bits_jit(chunk_bytes)
    
    if encrypt:
        # Pad to power of 2 for encryption
        padded_bits, original_bit_length = pad_to_power_of_2_jit(bits)
        current_bits = padded_bits.copy()
        
        # Apply shuffle
        if shuffle_type != 0:  # not 'none'
            # Map shuffle types to strings for existing shuffle function
            if shuffle_type == 1:
                current_bits = apply_in_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
            elif shuffle_type == 2:
                current_bits = apply_out_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
            elif shuffle_type == 3:
                current_bits = apply_milk_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
            elif shuffle_type == 4:
                current_bits = apply_cut_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
        
        # Apply transform
        current_bits = apply_transform_jit(current_bits, transform_type, transform_key)
        
        # Convert back to bytes
        result_bytes = bits_to_bytes_jit(current_bits)
        
    else:
        # For decryption: use bits as-is
        current_bits = bits.copy()
        
        # Apply inverse transform (transforms are self-inverse)
        current_bits = apply_transform_jit(current_bits, transform_type, transform_key)
        
        # Apply inverse shuffle
        if shuffle_type != 0:  # not 'none'
            if shuffle_type == 1:
                current_bits = apply_inverse_in_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
            elif shuffle_type == 2:
                current_bits = apply_inverse_out_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
            elif shuffle_type == 3:
                current_bits = apply_inverse_milk_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
            elif shuffle_type == 4:
                current_bits = apply_inverse_cut_shuffle_jit(current_bits, shuffle_steps, shuffle_variant)
        
        # Convert back to bytes and trim
        result_bytes = bits_to_bytes_jit(current_bits)
        
        # Trim to match input chunk size
        if len(result_bytes) > len(chunk_bytes):
            trimmed_result = np.zeros(len(chunk_bytes), dtype=np.uint8)
            trimmed_result[:] = result_bytes[:len(chunk_bytes)]
            result_bytes = trimmed_result
    
    return result_bytes

# JIT-optimized shuffle implementations
@njit
def apply_in_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized in-shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    
    for step in range(steps):
        temp = result.copy()
        mid = n // 2
        
        if variant == 0:
            even_positions = n - mid
            odd_positions = mid
            result[0::2] = temp[:even_positions]
            result[1::2] = temp[even_positions:even_positions+odd_positions]
        elif variant == 1:
            even_positions = n - mid
            odd_positions = mid
            result[0::2] = temp[mid:mid+even_positions]
            result[1::2] = temp[:odd_positions]
        elif variant == 2:
            even_positions = n - mid
            odd_positions = mid
            result[1::2] = temp[:odd_positions]
            result[0::2] = temp[odd_positions:odd_positions+even_positions]
        elif variant == 3:
            even_positions = n - mid
            odd_positions = mid
            result[1::2] = temp[even_positions:even_positions+odd_positions]
            result[0::2] = temp[:even_positions]
    
    return result

@njit
def apply_inverse_in_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized inverse in-shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    
    for step in range(steps - 1, -1, -1):
        temp = result.copy()
        mid = n // 2
        
        if variant == 0:
            even_positions = n - mid
            odd_positions = mid
            result[:even_positions] = temp[0::2]
            result[even_positions:even_positions+odd_positions] = temp[1::2]
        elif variant == 1:
            even_positions = n - mid
            odd_positions = mid
            result[:odd_positions] = temp[1::2]
            result[mid:mid+even_positions] = temp[0::2]
        elif variant == 2:
            even_positions = n - mid
            odd_positions = mid
            result[:odd_positions] = temp[1::2]
            result[odd_positions:odd_positions+even_positions] = temp[0::2]
        elif variant == 3:
            even_positions = n - mid
            odd_positions = mid
            result[:even_positions] = temp[0::2]
            result[even_positions:even_positions+odd_positions] = temp[1::2]
    
    return result

@njit
def apply_out_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized out-shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    
    for step in range(steps):
        temp = result.copy()
        mid = n // 2
        
        if variant == 0:
            result[:mid] = temp[0::2][:mid]
            remaining = n - mid
            result[mid:] = temp[1::2][:remaining]
        elif variant == 1:
            result[:mid] = temp[1::2][:mid]
            remaining = n - mid
            result[mid:] = temp[0::2][:remaining]
        elif variant == 2:
            result[1::2] = temp[:mid]
            result[0::2] = temp[mid:]
        elif variant == 3:
            result[0::2] = temp[mid:]
            result[1::2] = temp[:mid]
    
    return result

@njit
def apply_inverse_out_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized inverse out-shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    
    for step in range(steps - 1, -1, -1):
        temp = result.copy()
        mid = n // 2
        
        if variant == 0:
            result[0::2] = temp[:mid]
            result[1::2] = temp[mid:]
        elif variant == 1:
            result[1::2] = temp[:mid]
            result[0::2] = temp[mid:]
        elif variant == 2:
            result[:mid] = temp[1::2]
            result[mid:] = temp[0::2]
        elif variant == 3:
            result[mid:] = temp[0::2]
            result[:mid] = temp[1::2]
    
    return result

@njit  
def apply_milk_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized milk shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    
    for step in range(steps):
        temp = result.copy()
        
        if variant == 0:
            for i in range(n):
                if i % 2 == 0:
                    result[i] = temp[i // 2]
                else:
                    result[i] = temp[n - 1 - i // 2]
        elif variant == 1:
            for i in range(n):
                if i % 2 == 0:
                    result[i] = temp[n - 1 - i // 2]
                else:
                    result[i] = temp[i // 2]
        elif variant == 2:
            for i in range(n):
                if (i + 1) % 2 == 0:
                    result[i] = temp[i // 2]
                else:
                    result[i] = temp[n - 1 - i // 2]
        elif variant == 3:
            for i in range(n):
                if (i + 1) % 2 == 0:
                    result[i] = temp[n - 1 - i // 2]
                else:
                    result[i] = temp[i // 2]
    
    return result

@njit
def apply_inverse_milk_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized inverse milk shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    
    for step in range(steps - 1, -1, -1):
        temp = result.copy()
        
        if variant == 0:
            for i in range(n):
                if i % 2 == 0:
                    temp[i // 2] = result[i]
                else:
                    temp[n - 1 - i // 2] = result[i]
        elif variant == 1:
            for i in range(n):
                if i % 2 == 0:
                    temp[n - 1 - i // 2] = result[i]
                else:
                    temp[i // 2] = result[i]
        elif variant == 2:
            for i in range(n):
                if (i + 1) % 2 == 0:
                    temp[i // 2] = result[i]
                else:
                    temp[n - 1 - i // 2] = result[i]
        elif variant == 3:
            for i in range(n):
                if (i + 1) % 2 == 0:
                    temp[n - 1 - i // 2] = result[i]
                else:
                    temp[i // 2] = result[i]
        
        result = temp
    
    return result

@njit
def apply_cut_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized cut shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    cut_size = 2 if n > 2 else 1
    
    for step in range(steps):
        temp = result.copy()
        
        if variant == 0:
            cut_pos = n // 2
            result[:cut_pos] = temp[cut_size:cut_size + cut_pos]
            result[cut_pos:cut_pos + cut_size] = temp[:cut_size]
            result[cut_pos + cut_size:] = temp[cut_size + cut_pos:]
        elif variant == 1:
            cut_pos = n // 2
            result[:cut_pos - cut_size] = temp[:cut_pos - cut_size]
            result[cut_pos - cut_size:cut_pos] = temp[n - cut_size:]
            result[cut_pos:] = temp[cut_pos - cut_size:n - cut_size]
        elif variant == 2:
            cut_pos = n // 2
            result[:cut_size] = temp[cut_pos:cut_pos + cut_size]
            result[cut_size:cut_pos + cut_size] = temp[:cut_pos]
            result[cut_pos + cut_size:] = temp[cut_pos + cut_size:]
        elif variant == 3:
            cut_pos = n // 2
            result[:cut_pos] = temp[:cut_pos]
            result[cut_pos:n - cut_size] = temp[cut_pos + cut_size:]
            result[n - cut_size:] = temp[cut_pos:cut_pos + cut_size]
    
    return result

@njit
def apply_inverse_cut_shuffle_jit(bits: np.ndarray, steps: int, variant: int) -> np.ndarray:
    """JIT-optimized inverse cut shuffle"""
    result = bits.copy()
    n = len(result)
    
    if n <= 1:
        return result
    
    variant = variant % 4
    cut_size = 2 if n > 2 else 1
    
    for step in range(steps - 1, -1, -1):
        temp = result.copy()
        
        if variant == 0:
            cut_pos = n // 2
            temp[:cut_size] = result[cut_pos:cut_pos + cut_size]
            temp[cut_size:cut_size + cut_pos] = result[:cut_pos]
            temp[cut_size + cut_pos:] = result[cut_pos + cut_size:]
        elif variant == 1:
            cut_pos = n // 2
            temp[:cut_pos - cut_size] = result[:cut_pos - cut_size]
            temp[cut_pos - cut_size:n - cut_size] = result[cut_pos:]
            temp[n - cut_size:] = result[cut_pos - cut_size:cut_pos]
        elif variant == 2:
            cut_pos = n // 2
            temp[:cut_pos] = result[cut_size:cut_pos + cut_size]
            temp[cut_pos:cut_pos + cut_size] = result[:cut_size]
            temp[cut_pos + cut_size:] = result[cut_pos + cut_size:]
        elif variant == 3:
            cut_pos = n // 2
            temp[:cut_pos] = result[:cut_pos]
            temp[cut_pos:cut_pos + cut_size] = result[n - cut_size:]
            temp[cut_pos + cut_size:] = result[cut_pos:n - cut_size]
        
        result = temp
    
    return result

# Transform type mapping for optimization
TRANSFORM_TYPE_MAP = {
    'enhanced_xor': 0,
    'fibonacci': 1,
    'avalanche_cascade': 2,
    'prime_sieve': 3,
    'invert': 4,
    'swap_pairs': 5,
    'bit_flip': 6
}

SHUFFLE_TYPE_MAP = {
    'none': 0,
    'in': 1,
    'out': 2,
    'milk': 3,
    'cut': 4
} 