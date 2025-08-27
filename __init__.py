"""
Faro Cipher - Experimental encryption based on card shuffling algorithms

This package implements an encryption scheme using Faro (riffle) shuffle
permutations applied to data in binary and base64 domains.
"""

from .faro_cipher_improved import FaroCipher, EncryptionMetadata

__version__ = "2.0.0"
__author__ = "Faro Cipher Team"
__license__ = "WTFPL"

__all__ = ["FaroCipher", "EncryptionMetadata"] 