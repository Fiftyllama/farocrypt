"""
Faro Cipher: A research encryption system based on perfect shuffles and bit transforms
"""

from .core import FaroCipher, EncryptionMetadata
from .optimized import OptimizedFaroCipher, MemoryPool, ChunkBatch
from .jit_cipher import JITFaroCipher
from .ultra_cipher import UltraFaroCipher
from .utils import pad_to_power_of_2, generate_key_fingerprint, verify_key_compatibility

__version__ = "1.0.0"
__author__ = "Faro Cipher Project"

# Import main classes
from .core import SecurityProfile

# Main exports
__all__ = [
    'FaroCipher',
    'SecurityProfile',
    'pad_to_power_of_2',
    'OptimizedFaroCipher',
    'JITFaroCipher',
    'UltraFaroCipher',
    'EncryptionMetadata',
    'MemoryPool',
    'ChunkBatch',
    'generate_key_fingerprint',
    'verify_key_compatibility'
] 