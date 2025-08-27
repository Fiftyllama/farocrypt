"""
Faro Cipher Transform Functions
==============================

Transform functions for bit manipulation in the Faro Cipher.
All transforms are self-inverse (applying twice returns original data).
"""

import numpy as np

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
def enhanced_xor_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Enhanced XOR transform with key-dependent pattern.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    n = len(result)
    
    for i in range(n):
        # Create key-dependent pattern
        pattern = (key + i * 7) % 256
        if pattern % 3 == 0:
            result[i] = 1 - result[i]  # Flip bit
    
    return result

@njit
def fibonacci_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Fibonacci-based transform pattern.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    n = len(result)
    
    if n < 2:
        return result
    
    # Generate Fibonacci-like sequence starting with key
    fib_a, fib_b = key % 100, (key // 100) % 100
    
    for i in range(n):
        if fib_a % 4 == 0:
            result[i] = 1 - result[i]
        
        # Next Fibonacci number
        fib_a, fib_b = fib_b, (fib_a + fib_b) % 1000
    
    return result

@njit
def avalanche_cascade_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Simple self-inverse transform with key-dependent bit flipping.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    n = len(result)
    
    if n == 0:
        return result
    
    # Simple key-dependent bit flipping (guaranteed self-inverse)
    for i in range(n):
        # Create multiple key-dependent patterns for good diffusion
        pattern1 = (key + i * 7) % 256
        pattern2 = (key * 3 + i * 13) % 256
        pattern3 = (key ^ (i * 17)) % 256
        
        # Flip bit if any of several conditions are met
        # Each condition is applied identically on both passes, so it's self-inverse
        if (pattern1 % 8 == 0) or (pattern2 % 7 == 1) or (pattern3 % 9 == 3):
            result[i] = 1 - result[i]
    
    return result

@njit
def prime_sieve_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Prime number sieve-based transform.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    n = len(result)
    
    # Simple prime check for positions
    base_prime = 2 + (key % 97)  # Start with a prime near key
    
    for i in range(n):
        pos = i + base_prime
        # Simple primality test
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
    
    return result

@njit
def invert_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Simple invert transform with key pattern.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    
    for i in range(len(result)):
        if (i + key) % 3 == 0:
            result[i] = 1 - result[i]
    
    return result

@njit
def swap_pairs_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Swap adjacent pairs based on key pattern.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    
    for i in range(0, len(result) - 1, 2):
        if (i + key) % 4 == 0:
            result[i], result[i + 1] = result[i + 1], result[i]
    
    return result

@njit
def bit_flip_transform(bits: np.ndarray, key: int) -> np.ndarray:
    """
    Flip bits at key-determined positions.
    Self-inverse: applying twice returns original data.
    """
    result = bits.copy()
    
    for i in range(len(result)):
        if (i * key) % 7 == 0:
            result[i] = 1 - result[i]
    
    return result

# Available transforms registry
AVAILABLE_TRANSFORMS = {
    'enhanced_xor': enhanced_xor_transform,
    'fibonacci': fibonacci_transform,
    'avalanche_cascade': avalanche_cascade_transform,
    'prime_sieve': prime_sieve_transform,
    'invert': invert_transform,
    'swap_pairs': swap_pairs_transform,
    'bit_flip': bit_flip_transform,
}

def get_transform_function(name: str):
    """Get transform function by name"""
    return AVAILABLE_TRANSFORMS.get(name)

def list_available_transforms():
    """List all available transform names"""
    return list(AVAILABLE_TRANSFORMS.keys()) 