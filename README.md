# Warning, vibecoded slop

# Faro Cipher - High-Performance File Encryption

A high-performance file encryption system based on the Faro shuffle (card shuffling technique) applied to bit arrays. Built for algorithmic performance optimization and cryptographic research.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/faro-cipher.git
cd faro-cipher

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Usage

```python
from faro_cipher import FaroCipher

# Create cipher with your secret key
cipher = FaroCipher(key=b"your-secret-key", profile="balanced")

# Encrypt data
message = "Hello, Faro Cipher! This is a secret message."
encrypted_result = cipher.encrypt(message)

# Decrypt data
decrypted_data = cipher.decrypt(encrypted_result)
print(decrypted_data.decode('utf-8'))  # "Hello, Faro Cipher! This is a secret message."
```

### File Encryption

```python
# Encrypt a file
metadata = cipher.encrypt_file("document.txt", "document.encrypted")

# Decrypt the file
success = cipher.decrypt_file("document.encrypted", "document_restored.txt", metadata)
```

## 🛡️ Security Profiles

Choose the right profile for your needs:

- **Performance**: 3 rounds, fast encryption for non-sensitive data
- **Balanced**: 6 rounds, good balance of security and speed ⭐ *Recommended*
- **Maximum**: 12 rounds, maximum security for sensitive data

```python
# Different security levels
fast_cipher = FaroCipher(key=b"key", profile="performance")
balanced_cipher = FaroCipher(key=b"key", profile="balanced")  
secure_cipher = FaroCipher(key=b"key", profile="maximum")
```

## 🔧 Features

### ✅ Reliable Shuffle Variants
- **14 reliable shuffle variants** discovered through comprehensive testing
- Only uses verified shuffle algorithms (excludes problematic double shuffle variants 1, 3)
- **None**: 4 variants | **In**: 4 variants | **Out**: 4 variants | **Double**: 2 variants

### 🎯 Advanced Transforms
- **Enhanced XOR**: Key-dependent bit flipping patterns
- **Fibonacci**: Fibonacci sequence-based transformations
- **Avalanche Cascade**: High diffusion for security
- **Prime Sieve**: Prime number-based bit operations
- All transforms are **self-inverse** (applying twice returns original data)

### 🚀 Performance Optimized
- **Numba JIT compilation** for maximum speed
- **Chunked processing** for large files
- **Configurable chunk sizes** for different use cases
- **Memory efficient** streaming operations

### 🔒 Security Features
- **PBKDF2 key derivation** with variable iterations
- **Key fingerprinting** for metadata verification
- **Perfect round-trip encryption** (no data loss)
- **Deterministic structure generation** from keys

## 📋 Examples

Run the included examples to see Faro Cipher in action:

```bash
# Basic usage examples
python examples/basic_usage.py

# File encryption examples
python examples/file_encryption.py
```

## 🧪 Testing

Run the test suite to verify everything works correctly:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_core.py
```

## 📊 Project Structure

```
faro-cipher/
├── faro_cipher/           # Main package
│   ├── __init__.py        # Package exports
│   ├── core.py            # Main FaroCipher class
│   ├── shuffles.py        # Shuffle algorithms
│   ├── transforms.py      # Transform functions
│   ├── utils.py           # Utility functions
│   └── legacy.py          # Legacy implementation info
├── examples/              # Usage examples
│   ├── basic_usage.py     # Basic encryption examples
│   └── file_encryption.py # File encryption examples
├── tests/                 # Test suite
│   └── test_core.py       # Core functionality tests
├── docs/                  # Documentation
├── archive/               # Historical implementations
├── setup.py               # Package installation
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## 🔍 Research & Development

This project emerged from extensive research into shuffle algorithms and cryptographic properties:

### Key Discoveries
1. **Shuffle Reliability**: Only 14 out of 16 shuffle variants are reliable
2. **Data Flow Issues**: Fixed critical data corruption from improper trimming
3. **Transform-Driven Security**: Security comes primarily from transforms, not shuffles
4. **Performance vs Security**: Identified optimal trade-offs for different use cases

### Security Analysis
- **Avalanche Effect**: Measures how single-bit changes affect output
- **Key Sensitivity**: Ensures different keys produce different results  
- **Round Scaling**: More rounds generally improve security
- **Comprehensive Testing**: All operations verified through extensive testing

## ⚠️ Security Disclaimer

**For Educational and Research Purposes**: This cipher is designed for learning about encryption algorithms and performance optimization. While it implements sound cryptographic principles, it has not undergone formal security review. 

**Not recommended for production security applications** without professional cryptographic audit.

## 🛠️ Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Requirements
- Python 3.8+
- NumPy for array operations
- Numba for JIT compilation (optional, but recommended for performance)

## 📜 License

**WTFPL v2** - Do whatever you want with this code!

*"Do whatever you want. Copy it on physical media and burn it, change it and use it to take over the world, break it with hammers, fix it so you can arrest people, sell it for drugs, use it to arrest people with hammers, it's your problem now. Don't blame me if it sets your cat on fire."*

See the [LICENSE](LICENSE) file for full details, or visit http://www.wtfpl.net/

SPDX-License-Identifier: WTFPL

## 🎯 Use Cases

### ✅ Great For:
- **Learning cryptography** and algorithm design
- **Performance research** and optimization studies
- **Non-sensitive data obfuscation**
- **Algorithm prototyping** and experimentation

### ❌ Not Suitable For:
- Production security applications (without audit)
- Highly sensitive data protection
- Compliance with cryptographic standards
- Mission-critical security requirements

## 🚀 Performance

Benchmarks on typical hardware:
- **Performance Profile**: ~0.9 MB/s, 3 rounds
- **Balanced Profile**: ~0.7 MB/s, 6 rounds  
- **Maximum Profile**: ~0.4 MB/s, 12 rounds

*Performance varies based on hardware and data characteristics*

