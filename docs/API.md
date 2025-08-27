# 📚 Faro Cipher API Documentation

Complete API reference for the Faro Cipher encryption system.

**License**: WTFPL v2 - Do whatever you want with this code!

## 🚀 Quick Start

```python
from faro_cipher import FaroCipher, UltraFaroCipher

# Standard cipher
cipher = FaroCipher(key=b"your-secret-key", profile="balanced")

# Ultra-optimized cipher (recommended)
ultra_cipher = UltraFaroCipher(key=b"your-secret-key", profile="balanced")
```

## 📦 Package Structure

```python
from faro_cipher import (
    FaroCipher,           # Standard implementation
    UltraFaroCipher,      # Ultra-optimized implementation  
    EncryptionMetadata,   # Metadata class
    SecurityProfile       # Security configuration
)
```

---

## 🔧 Core API

### FaroCipher Class

**File**: `faro_cipher/core.py`

The standard Faro Cipher implementation with reliable shuffle variants and transform operations.

#### Constructor

```python
cipher = FaroCipher(
    key: bytes,
    profile: str = "balanced", 
    chunk_size: int = 8192,
    rounds: Optional[int] = None
)
```

**Parameters**:
- `key` (bytes): Encryption key
- `profile` (str): Security profile - "performance", "balanced", or "maximum"
- `chunk_size` (int): Chunk size for processing (default: 8192)
- `rounds` (Optional[int]): Override profile rounds (1-100)

**Security Profiles**:
- **"performance"**: 3 rounds, fast encryption for non-sensitive data
- **"balanced"**: 6 rounds, good balance of security and speed ⭐ *Recommended*
- **"maximum"**: 12 rounds, maximum security for sensitive data

**Example**:
```python
# Balanced security (recommended)
cipher = FaroCipher(key=b"my-secret-key", profile="balanced")

# Custom configuration  
cipher = FaroCipher(key=b"my-key", profile="performance", rounds=5, chunk_size=4096)
```

#### Methods

##### `encrypt(data: Union[bytes, str]) -> Dict[str, Any]`

Encrypts data using the Faro cipher algorithm.

**Parameters**:
- `data` (bytes or str): Data to encrypt

**Returns**:
- `dict`: Dictionary containing:
  - `encrypted_data` (bytes): Encrypted binary data
  - `metadata` (EncryptionMetadata): Encryption metadata

**Example**:
```python
message = "Hello, World!"
result = cipher.encrypt(message)
encrypted_data = result['encrypted_data']
metadata = result['metadata']
```

##### `decrypt(encrypted_result: Dict[str, Any]) -> bytes`

Decrypts data using the Faro cipher algorithm.

**Parameters**:
- `encrypted_result` (dict): Result from encrypt() method

**Returns**:
- `bytes`: Decrypted data

**Example**:
```python
decrypted_data = cipher.decrypt(result)
message = decrypted_data.decode('utf-8')
```

##### `encrypt_file(input_file: str, output_file: str) -> EncryptionMetadata`

Encrypts a file using variable chunk sizes.

**Parameters**:
- `input_file` (str): Path to input file
- `output_file` (str): Path to output encrypted file

**Returns**:
- `EncryptionMetadata`: File encryption metadata

**Example**:
```python
metadata = cipher.encrypt_file("document.txt", "document.enc")
```

##### `decrypt_file(input_file: str, output_file: str, metadata: EncryptionMetadata) -> bool`

Decrypts a file.

**Parameters**:
- `input_file` (str): Path to encrypted file
- `output_file` (str): Path to output decrypted file  
- `metadata` (EncryptionMetadata): Encryption metadata

**Returns**:
- `bool`: True if successful, False otherwise

**Example**:
```python
success = cipher.decrypt_file("document.enc", "document_restored.txt", metadata)
```

##### `get_info() -> Dict[str, Any]`

Get cipher configuration information.

**Returns**:
- `dict`: Configuration details including profile, rounds, key fingerprint, etc.

---

## 🚀 Ultra-Optimized API

### UltraFaroCipher Class

**File**: `faro_cipher/ultra_cipher.py`

Ultra-high performance implementation with algorithmic optimizations.

**Performance Improvements**:
- 5-25x faster encryption/decryption
- 5x memory efficiency through virtual padding
- Cache-optimized processing for large data
- Streaming file processing without memory explosion

#### Constructor

```python
ultra_cipher = UltraFaroCipher(
    key: bytes,
    profile: str = "balanced",
    chunk_size: int = 8192, 
    rounds: Optional[int] = None,
    cache_optimize: bool = True
)
```

**Additional Parameters**:
- `cache_optimize` (bool): Enable cache optimization for large data (default: True)

**Example**:
```python
# Ultra cipher with cache optimization
ultra_cipher = UltraFaroCipher(key=b"secret-key", profile="balanced")

# Disable cache optimization for small data
ultra_cipher = UltraFaroCipher(key=b"secret-key", cache_optimize=False)
```

#### Enhanced Methods

All methods from `FaroCipher` plus:

##### `encrypt_file_ultra(input_file: str, output_file: str, chunk_size: int = 1024*1024, progress: bool = True) -> EncryptionMetadata`

Ultra-optimized streaming file encryption.

**Parameters**:
- `input_file` (str): Path to input file
- `output_file` (str): Path to output encrypted file
- `chunk_size` (int): Processing chunk size (default: 1MB)
- `progress` (bool): Show progress indicators (default: True)

**Returns**:
- `EncryptionMetadata`: Enhanced metadata with streaming information

**Example**:
```python
# Encrypt large file with progress
metadata = ultra_cipher.encrypt_file_ultra(
    "large_video.mp4", 
    "large_video.enc",
    chunk_size=2*1024*1024,  # 2MB chunks
    progress=True
)
```

##### `benchmark_ultra_vs_others(data_size: int = 1024*1024) -> Dict[str, float]`

Comprehensive performance benchmark.

**Parameters**:
- `data_size` (int): Test data size in bytes (default: 1MB)

**Returns**:
- `dict`: Throughput results for different implementations

**Example**:
```python
results = ultra_cipher.benchmark_ultra_vs_others(data_size=10*1024*1024)
print(f"Ultra throughput: {results['ultra']:.1f} MB/s")
```

##### `get_optimization_info() -> Dict[str, Any]`

Get detailed optimization information.

**Returns**:
- `dict`: Optimization details and expected performance improvements

---

## 📊 Metadata Classes

### EncryptionMetadata

**File**: `faro_cipher/core.py`

Stores encryption metadata for decryption and verification.

```python
@dataclass
class EncryptionMetadata:
    version: str
    profile: str
    rounds: int
    chunk_size: int
    round_structure: List[Dict[str, Any]]
    key_fingerprint: str
    original_size: Optional[int] = None
    chunk_sizes: Optional[List[int]] = None
```

**Attributes**:
- `version`: Cipher version identifier
- `profile`: Security profile used
- `rounds`: Number of encryption rounds
- `chunk_size`: Processing chunk size
- `round_structure`: Detailed round configuration
- `key_fingerprint`: Key verification fingerprint
- `original_size`: Original data size (for trimming)
- `chunk_sizes`: Chunk sizes for file encryption

### SecurityProfile

**File**: `faro_cipher/core.py`

Static methods for security profile configurations.

```python
SecurityProfile.performance()  # Returns performance config
SecurityProfile.balanced()     # Returns balanced config  
SecurityProfile.maximum()      # Returns maximum config
```

---

## 🎯 Algorithm Details

### Shuffle Variants

The cipher uses **14 reliable shuffle variants** across 4 types:

- **None**: 4 variants (no shuffle, identity operations)
- **In**: 4 variants (in-shuffle variations)  
- **Out**: 4 variants (out-shuffle variations)
- **Milk**: 2 variants (milk-shuffle operations)
- **Cut**: 2 variants (cut-shuffle operations)

### Transform Functions

- **Enhanced XOR**: Key-dependent bit flipping patterns
- **Fibonacci**: Fibonacci sequence-based transformations
- **Avalanche Cascade**: High diffusion for security
- **Prime Sieve**: Prime number-based bit operations
- **Invert**: Bit inversion operations
- **Swap Pairs**: Adjacent bit pair swapping
- **Bit Flip**: Controlled bit flipping

All transforms are **self-inverse** (applying twice returns original data).

### Round Structure

Each round applies:
1. **Shuffle operation** with configurable steps and variants
2. **Transform operation** with key-derived parameters
3. **Variable chunk processing** for optimal diffusion

---

## 🔒 Security Features

### Key Derivation
- **PBKDF2** with SHA256 
- Variable iterations (10,000 + rounds × 1,000)
- Salt: "FaroCipherEntropy2024"

### Key Fingerprinting
```python
fingerprint = generate_key_fingerprint(key)  # 16-character hex
verify_key_compatibility(key, fingerprint)   # Returns bool
```

### Entropy Optimization
- **Round entropy scoring** based on shuffle and transform complexity
- **Multi-scale diffusion** with variable chunk sizes
- **Balanced operation distribution** across rounds

---

## ⚡ Performance Tips

### Standard Implementation
- Use `chunk_size=4096` for small files
- Use `chunk_size=16384` for large files
- Choose appropriate security profile

### Ultra Implementation  
- Enable `cache_optimize=True` for files > 64KB
- Use `encrypt_file_ultra()` for large files
- Monitor memory usage with progress indicators

### Benchmarking
```python
# Quick benchmark
results = ultra_cipher.benchmark_ultra_vs_others(1024*1024)

# Detailed optimization analysis
ultra_cipher.analyze_optimization_impact(1024*1024)
```

---

## 🚨 Error Handling

### Common Exceptions

```python
# Key mismatch during decryption
ValueError("Key fingerprint mismatch - wrong key or corrupted metadata")

# Invalid configuration
ValueError("Rounds must be at least 1")
ValueError("Maximum 100 rounds supported")
ValueError("Unknown profile: invalid_profile")

# File operations
FileNotFoundError  # Missing input files
PermissionError    # File access issues
```

### Best Practices

```python
try:
    # Always verify decryption success
    decrypted_data = cipher.decrypt(encrypted_result)
    
    # Verify file operations
    if not cipher.decrypt_file(input_file, output_file, metadata):
        print("Decryption failed!")
        
except ValueError as e:
    print(f"Cipher error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 🧪 Testing

### Basic Functionality Test
```python
# Round-trip test
original_data = b"Test message"
encrypted_result = cipher.encrypt(original_data)
decrypted_data = cipher.decrypt(encrypted_result)
assert decrypted_data == original_data
```

### Performance Test
```python
import time

data = os.urandom(1024*1024)  # 1MB test data
start_time = time.perf_counter()
encrypted_result = cipher.encrypt(data)
decrypted_data = cipher.decrypt(encrypted_result)
elapsed = time.perf_counter() - start_time

throughput = (len(data) * 2) / (1024 * 1024 * elapsed)
print(f"Throughput: {throughput:.1f} MB/s")
```

---

## 📝 Examples

See the project's `examples/` directory and `test_release.py` for comprehensive usage examples.

**API Version**: 1.0.0  
**Last Updated**: 2024  
**License**: WTFPL v2 