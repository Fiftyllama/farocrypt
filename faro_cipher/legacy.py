"""
Legacy Faro Cipher Implementations
==================================

Legacy implementations kept for compatibility and research purposes.
These include the original ultra-optimized and streamlined implementations.
"""

# For now, this is a placeholder for potential legacy support
# The original implementations are preserved in the archive/ directory

def get_legacy_implementations():
    """Get list of available legacy implementations"""
    return [
        "faro_cipher_ultra_optimized.py",
        "faro_cipher_streamlined.py", 
        "robust_faro_cipher.py",
        "enhanced_robust_faro_cipher.py",
        "faro_cipher_key_controlled.py"
    ]

def get_legacy_info():
    """Get information about legacy implementations"""
    return {
        "ultra_optimized": {
            "description": "Champion implementation from comprehensive analysis",
            "security": "Excellent (0.497 avalanche effect)",
            "performance": "Good (0.70 MB/s)",
            "status": "Archived - superseded by new package structure"
        },
        "streamlined": {
            "description": "Fast but cryptographically insecure implementation", 
            "security": "Poor (0.003 avalanche effect)",
            "performance": "Excellent (0.94 MB/s)",
            "status": "Archived - use only for performance research"
        },
        "robust": {
            "description": "Reliable implementation with verified shuffle variants",
            "security": "Good (uses only reliable shuffles)",
            "performance": "Good",
            "status": "Archived - functionality integrated into new core"
        }
    } 