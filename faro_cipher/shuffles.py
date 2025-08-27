"""
Faro Cipher Shuffle Functions
============================

Reliable shuffle implementations for the Faro Cipher.
Only includes variants that have been verified as reliable.
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

# Reliable shuffle variants discovered through comprehensive testing
RELIABLE_SHUFFLE_VARIANTS = {
    'none': [0, 1, 2, 3],      # All variants work (no shuffling)
    'in': [0, 1, 2, 3],        # All variants work
    'out': [0, 1, 2, 3],       # All variants work
    'milk': [0, 1, 2, 3],      # Milk shuffle variants (alternating top/bottom)
    'cut': [0, 1, 2, 3]        # Two-card cut variants
}

@njit
def faro_shuffle(bits: np.ndarray, shuffle_type: str, steps: int, variant: int) -> np.ndarray:
    """
    Apply Faro shuffle to bit array using only reliable variants.
    
    Args:
        bits: Input bit array
        shuffle_type: Type of shuffle ('none', 'in', 'out', 'milk', 'cut')
        steps: Number of shuffle steps to apply
        variant: Shuffle variant (must be reliable for the shuffle type)
        
    Returns:
        Shuffled bit array
    """
    result = bits.copy()
    n = len(result)
    
    if n <= 1 or shuffle_type == 'none':
        return result
    
    # Force variant to be reliable for the shuffle type
    if shuffle_type == 'milk' or shuffle_type == 'cut':
        variant = variant % 4  # Ensure valid variant number
    else:
        variant = variant % 4  # Ensure valid variant number
    
    for step in range(steps):
        temp = result.copy()
        mid = n // 2
        
        if shuffle_type == "in":
            # In-shuffle variants
            if variant == 0:  # Standard in-shuffle
                even_positions = n - mid
                odd_positions = mid
                result[0::2] = temp[:even_positions]
                result[1::2] = temp[even_positions:even_positions+odd_positions]
            elif variant == 1:  # Reversed in-shuffle
                even_positions = n - mid
                odd_positions = mid
                result[0::2] = temp[mid:mid+even_positions]
                result[1::2] = temp[:odd_positions]
            elif variant == 2:  # Offset in-shuffle
                even_positions = n - mid
                odd_positions = mid
                result[1::2] = temp[:odd_positions]
                result[0::2] = temp[odd_positions:odd_positions+even_positions]
            elif variant == 3:  # Reverse offset in-shuffle
                even_positions = n - mid
                odd_positions = mid
                result[1::2] = temp[even_positions:even_positions+odd_positions]
                result[0::2] = temp[:even_positions]
                
        elif shuffle_type == "out":
            # Out-shuffle variants
            if variant == 0:  # Standard out-shuffle
                result[:mid] = temp[0::2][:mid]
                remaining = n - mid
                result[mid:] = temp[1::2][:remaining]
            elif variant == 1:  # Reversed out-shuffle
                result[:mid] = temp[1::2][:mid]
                remaining = n - mid
                result[mid:] = temp[0::2][:remaining]
            elif variant == 2:  # Offset out-shuffle
                result[1::2] = temp[:mid]
                result[0::2] = temp[mid:]
            elif variant == 3:  # Reverse offset out-shuffle
                result[0::2] = temp[mid:]
                result[1::2] = temp[:mid]
                
        elif shuffle_type == "milk":
            # Milk shuffle - alternate taking from top and bottom
            if variant == 0:
                # Standard milk: top, bottom, top, bottom...
                for i in range(n):
                    if i % 2 == 0:
                        result[i] = temp[i // 2]  # Take from top half
                    else:
                        result[i] = temp[n - 1 - i // 2]  # Take from bottom half
            elif variant == 1:
                # Reverse milk: bottom, top, bottom, top...
                for i in range(n):
                    if i % 2 == 0:
                        result[i] = temp[n - 1 - i // 2]  # Take from bottom half
                    else:
                        result[i] = temp[i // 2]  # Take from top half
            elif variant == 2:
                # Offset milk: start from position 1
                for i in range(n):
                    if (i + 1) % 2 == 0:
                        result[i] = temp[i // 2]
                    else:
                        result[i] = temp[n - 1 - i // 2]
            elif variant == 3:
                # Reverse offset milk
                for i in range(n):
                    if (i + 1) % 2 == 0:
                        result[i] = temp[n - 1 - i // 2]
                    else:
                        result[i] = temp[i // 2]
                
        elif shuffle_type == "cut":
            # Two-card cut - move 2 cards from one position to another
            cut_size = 2 if n > 2 else 1
            if variant == 0:
                # Cut from top, insert in middle
                cut_pos = n // 2
                result[:cut_pos] = temp[cut_size:cut_size + cut_pos]
                result[cut_pos:cut_pos + cut_size] = temp[:cut_size]
                result[cut_pos + cut_size:] = temp[cut_size + cut_pos:]
            elif variant == 1:
                # Cut from bottom, insert in middle
                cut_pos = n // 2
                result[:cut_pos - cut_size] = temp[:cut_pos - cut_size]
                result[cut_pos - cut_size:cut_pos] = temp[n - cut_size:]
                result[cut_pos:] = temp[cut_pos - cut_size:n - cut_size]
            elif variant == 2:
                # Cut from middle, move to top
                cut_pos = n // 2
                result[:cut_size] = temp[cut_pos:cut_pos + cut_size]
                result[cut_size:cut_pos + cut_size] = temp[:cut_pos]
                result[cut_pos + cut_size:] = temp[cut_pos + cut_size:]
            elif variant == 3:
                # Cut from middle, move to bottom
                cut_pos = n // 2
                result[:cut_pos] = temp[:cut_pos]
                result[cut_pos:n - cut_size] = temp[cut_pos + cut_size:]
                result[n - cut_size:] = temp[cut_pos:cut_pos + cut_size]
    
    return result

@njit
def inverse_faro_shuffle(bits: np.ndarray, shuffle_type: str, steps: int, variant: int) -> np.ndarray:
    """
    Apply inverse Faro shuffle to reverse the shuffle operation.
    
    Args:
        bits: Input bit array (shuffled)
        shuffle_type: Type of shuffle used ('none', 'in', 'out', 'milk', 'cut')
        steps: Number of shuffle steps to reverse
        variant: Shuffle variant used
        
    Returns:
        Unshuffled bit array
    """
    result = bits.copy()
    n = len(result)
    
    if n <= 1 or shuffle_type == 'none':
        return result
    
    # Force variant to be reliable
    if shuffle_type == 'milk' or shuffle_type == 'cut':
        variant = variant % 4
    else:
        variant = variant % 4
    
    # Apply inverse shuffles in reverse order
    for step in range(steps - 1, -1, -1):
        temp = result.copy()
        mid = n // 2
        
        if shuffle_type == "in":
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
                
        elif shuffle_type == "out":
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
                
        elif shuffle_type == "milk":
            # Inverse milk shuffle - reverse the milk shuffle operation
            if variant == 0:
                # Inverse of standard milk
                for i in range(n):
                    if i % 2 == 0:
                        result[i // 2] = temp[i]  # Put back to top half
                    else:
                        result[n - 1 - i // 2] = temp[i]  # Put back to bottom half
            elif variant == 1:
                # Inverse of reverse milk
                for i in range(n):
                    if i % 2 == 0:
                        result[n - 1 - i // 2] = temp[i]  # Put back to bottom half
                    else:
                        result[i // 2] = temp[i]  # Put back to top half
            elif variant == 2:
                # Inverse of offset milk
                for i in range(n):
                    if (i + 1) % 2 == 0:
                        result[i // 2] = temp[i]
                    else:
                        result[n - 1 - i // 2] = temp[i]
            elif variant == 3:
                # Inverse of reverse offset milk
                for i in range(n):
                    if (i + 1) % 2 == 0:
                        result[n - 1 - i // 2] = temp[i]
                    else:
                        result[i // 2] = temp[i]
                
        elif shuffle_type == "cut":
            # Inverse two-card cut - reverse the cut operation
            cut_size = 2 if n > 2 else 1
            if variant == 0:
                # Inverse: move cards back from middle to top
                cut_pos = n // 2
                result[:cut_size] = temp[cut_pos:cut_pos + cut_size]
                result[cut_size:cut_size + cut_pos] = temp[:cut_pos]
                result[cut_size + cut_pos:] = temp[cut_pos + cut_size:]
            elif variant == 1:
                # Inverse: move cards back from middle to bottom
                cut_pos = n // 2
                result[:cut_pos - cut_size] = temp[:cut_pos - cut_size]
                result[n - cut_size:] = temp[cut_pos - cut_size:cut_pos]
                result[cut_pos - cut_size:n - cut_size] = temp[cut_pos:]
            elif variant == 2:
                # Inverse: move cards back from top to middle
                cut_pos = n // 2
                result[:cut_pos] = temp[cut_size:cut_pos + cut_size]
                result[cut_pos:cut_pos + cut_size] = temp[:cut_size]
                result[cut_pos + cut_size:] = temp[cut_pos + cut_size:]
            elif variant == 3:
                # Inverse: move cards back from bottom to middle
                cut_pos = n // 2
                result[:cut_pos] = temp[:cut_pos]
                result[cut_pos:cut_pos + cut_size] = temp[n - cut_size:]
                result[cut_pos + cut_size:] = temp[cut_pos:n - cut_size]
    
    return result

def get_reliable_variants(shuffle_type: str) -> list:
    """Get list of reliable variants for a shuffle type"""
    return RELIABLE_SHUFFLE_VARIANTS.get(shuffle_type, []) 