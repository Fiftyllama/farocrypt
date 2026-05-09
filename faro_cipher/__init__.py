"""
faro_cipher — encryption via faro shuffles and bit transforms.
"""

from .core import FaroCipher, EncryptionMetadata, SecurityProfile
from .utils import generate_key_fingerprint, verify_key_compatibility

__version__ = "2.0.0"
__all__ = [
    'FaroCipher',
    'EncryptionMetadata',
    'SecurityProfile',
    'generate_key_fingerprint',
    'verify_key_compatibility',
]
