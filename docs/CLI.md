# 👑 Cliopatra - Faro Cipher CLI Documentation

**Cliopatra** is the command-line interface for the Faro Cipher, named after the legendary queen who mastered the art of codes and ciphers. It provides ultra-optimized performance with professional-grade tooling.

**License**: WTFPL v2 - Do whatever you want with this code!

## 🚀 Quick Start

```bash
# Encrypt text with ultra performance (default)
python cliopatra.py encrypt-text --key "my-secret-key" --text "Hello, World!"

# Encrypt a file
python cliopatra.py encrypt-file --key "my-secret-key" -i document.pdf -o document.enc

# Show cipher information
python cliopatra.py info --key "my-secret-key"

# Benchmark performance
python cliopatra.py benchmark --key "my-secret-key"
```

## 📋 Command Overview

| Command | Description |
|---------|-------------|
| `encrypt-text` | Encrypt text data |
| `decrypt-text` | Decrypt text data |
| `encrypt-file` | Encrypt a file |
| `decrypt-file` | Decrypt a file |
| `info` | Show cipher information |
| `benchmark` | Performance benchmarking |

## 🎯 Global Options

### Key Management
```bash
--key "your-key"          # Provide key directly (not recommended for production)
--key-file /path/to/key   # Read key from file
# (if neither provided, you'll be prompted securely)
```

### Security Profiles
```bash
--profile performance     # 3 rounds, fast encryption
--profile balanced       # 6 rounds, good balance (default)
--profile maximum        # 12 rounds, maximum security
```

### Implementation Choice
```bash
--standard               # Use standard implementation
# (default: ultra-optimized for maximum performance)
```

### Advanced Options
```bash
--rounds N               # Custom rounds (1-100, overrides profile)
--no-cache              # Disable cache optimization (ultra only)
--force                 # Force operation despite warnings
--verbose               # Verbose output
```

---

## 🔐 Text Encryption Commands

### encrypt-text

Encrypt text data with ultra-optimized performance.

```bash
python cliopatra.py encrypt-text [options]
```

**Options**:
- `--text "message"` or `-t "message"`: Text to encrypt
- `--output file.json` or `-o file.json`: Save to JSON file
- (If no text provided, reads from stdin)

**Examples**:
```bash
# Encrypt text directly
python cliopatra.py encrypt-text --key "secret" --text "Hello, World!"

# Encrypt from stdin
echo "Secret message" | python cliopatra.py encrypt-text --key "secret"

# Save to file
python cliopatra.py encrypt-text --key "secret" -t "Message" -o encrypted.json

# Maximum security
python cliopatra.py encrypt-text --key "secret" --profile maximum -t "Top Secret"
```

**Output Formats**:
- **Console**: Hex-encoded encrypted data + metadata
- **File**: JSON format with base64-encoded data and metadata

### decrypt-text

Decrypt text data.

```bash
python cliopatra.py decrypt-text [options]
```

**Options**:
- `--input file.json` or `-i file.json`: Input JSON file
- `--output file.txt` or `-o file.txt`: Save decrypted text
- (If no input file, reads hex from stdin)

**Examples**:
```bash
# Decrypt from JSON file
python cliopatra.py decrypt-text --key "secret" -i encrypted.json

# Decrypt hex input
python cliopatra.py decrypt-text --key "secret"
# (then paste hex when prompted)

# Save to file
python cliopatra.py decrypt-text --key "secret" -i encrypted.json -o message.txt
```

---

## 📁 File Encryption Commands

### encrypt-file

Encrypt files with streaming ultra-optimization for any file size.

```bash
python cliopatra.py encrypt-file -i input_file -o output_file [options]
```

**Required Options**:
- `--input file` or `-i file`: Input file to encrypt
- `--output file` or `-o file`: Output encrypted file

**Examples**:
```bash
# Basic file encryption
python cliopatra.py encrypt-file --key "secret" -i document.pdf -o document.enc

# Large file with progress
python cliopatra.py encrypt-file --key "secret" -i movie.mp4 -o movie.enc

# Maximum security
python cliopatra.py encrypt-file --key "secret" --profile maximum -i sensitive.docx -o sensitive.enc

# Standard implementation
python cliopatra.py --standard encrypt-file --key "secret" -i file.txt -o file.enc
```

**Output Files**:
- `output_file`: Encrypted binary data
- `output_file.meta`: JSON metadata required for decryption

### decrypt-file

Decrypt files using metadata.

```bash
python cliopatra.py decrypt-file -i encrypted_file -o output_file [options]
```

**Required Options**:
- `--input file` or `-i file`: Encrypted input file
- `--output file` or `-o file`: Output decrypted file

**Examples**:
```bash
# Basic file decryption
python cliopatra.py decrypt-file --key "secret" -i document.enc -o document_restored.pdf

# Different cipher type warning (auto-detected)
python cliopatra.py --standard decrypt-file --key "secret" -i ultra_encrypted.enc -o file.txt
# Warning: File was encrypted with ultra cipher, but you're using standard cipher.

# Force decryption despite warnings
python cliopatra.py --standard decrypt-file --key "secret" -i ultra_encrypted.enc -o file.txt --force
```

**Metadata Files**:
- Automatically looks for `input_file.meta`
- Contains encryption parameters and verification data

---

## ℹ️ Information Commands

### info

Display detailed cipher configuration and optimization information.

```bash
python cliopatra.py info --key "your-key" [options]
```

**Example Output**:
```
Cliopatra - Faro Cipher Information
========================================
Implementation: Ultra-Optimized
Version: ultra_optimized_v1.0
Optimizations:
  • Byte-level operations (8x speedup)
  • Virtual padding (5x memory reduction)
  • Cache-optimized processing
  • Vectorized transforms
  • Streaming file processing
  • JIT compilation via Numba
Expected speedup: 5-10x over JIT, 20-50x over standard
Memory efficiency: 5x reduction vs bit-level operations
Profile: balanced
Description: Good balance of security and speed
Rounds: 6
Chunk size: 8192 bytes
Key fingerprint: 53136271c432a1af

Round Structure:
  Round 1: out + avalanche_cascade @ 2KB (entropy: 10.0)
  Round 2: in + enhanced_xor @ 8KB (entropy: 10.6)
  Round 3: cut + fibonacci @ 8KB (entropy: 12.2)
  Round 4: milk + bit_flip @ 16KB (entropy: 12.9)
  Round 5: none + prime_sieve @ 4KB (entropy: 8.7)
  Round 6: out + invert @ 4KB (entropy: 6.9)
```

---

## 🏁 Performance Commands

### benchmark

Comprehensive performance testing across different data sizes.

```bash
python cliopatra.py benchmark --key "your-key" [options]
```

**Test Sizes**: 1KB, 10KB, 100KB, 1MB

**Example Output**:
```
Cliopatra Performance Benchmark
========================================

Testing 1KB:
  Ultra Cipher:
    Round-trip: 0.015s (0.1 MB/s)
  Standard Cipher:
    Round-trip: 0.089s (0.0 MB/s)
    Ultra speedup: 5.9x

Testing 10KB:
  Ultra Cipher:
    Round-trip: 0.008s (2.5 MB/s)
  Standard Cipher:
    Round-trip: 0.052s (0.4 MB/s)
    Ultra speedup: 6.5x

Testing 100KB:
  Ultra Cipher:
    Round-trip: 0.012s (16.7 MB/s)
  Standard Cipher:
    Round-trip: 0.087s (2.3 MB/s)
    Ultra speedup: 7.3x

Testing 1MB:
  Ultra Cipher:
    Round-trip: 0.034s (58.8 MB/s)
  Standard Cipher:
    Round-trip: 0.421s (4.7 MB/s)
    Ultra speedup: 12.4x
```

---

## 🔒 Security Features

### Cipher Type Compatibility

Cliopatra automatically detects cipher type mismatches:

```bash
# File encrypted with ultra, trying to decrypt with standard
python cliopatra.py --standard decrypt-file -i ultra_file.enc -o output.txt
# Warning: File was encrypted with ultra cipher, but you're using standard cipher.
# Use --force to attempt decryption anyway, or use the matching cipher type.
```

### Key Security

```bash
# Secure key input (recommended)
python cliopatra.py encrypt-text
# Enter encryption key: [hidden input]

# Key from file (secure)
echo "my-secret-key" > keyfile
python cliopatra.py encrypt-text --key-file keyfile

# Command line key (not recommended for production)
python cliopatra.py encrypt-text --key "my-secret-key"
```

### Key Fingerprinting

All operations display key fingerprints for verification:
```
Key fingerprint: 53136271c432a1af
```

---

## ⚡ Performance Features

### Ultra Mode (Default)

**Enabled by default** for maximum performance:
- 5-25x faster than standard implementation
- Algorithmic optimizations with byte-level operations
- Cache optimization for large files
- Streaming processing without memory explosion

### Standard Mode

Use `--standard` flag for compatibility testing:
```bash
python cliopatra.py --standard encrypt-text --key "test" -t "message"
```

### Cache Optimization

Control cache behavior for ultra mode:
```bash
# Disable cache optimization
python cliopatra.py --no-cache encrypt-file -i large_file.bin -o output.enc

# Cache optimization automatically enabled for files > 64KB
```

---

## 🎛️ Configuration Examples

### Basic Usage Patterns

```bash
# Quick text encryption
python cliopatra.py encrypt-text --key "secret" --text "Hello!"

# Secure file encryption
python cliopatra.py encrypt-file --key-file keyfile --profile maximum -i sensitive.doc -o sensitive.enc

# Fast bulk processing
python cliopatra.py encrypt-file --key "key" --profile performance -i large_data.bin -o large_data.enc
```

### Advanced Workflows

```bash
# Custom security configuration
python cliopatra.py encrypt-file --key "secret" --rounds 8 -i document.pdf -o document.enc

# Cross-platform compatibility
python cliopatra.py --standard encrypt-file --key "secret" -i file.txt -o file.enc

# Performance analysis
python cliopatra.py benchmark --key "test-key" --profile maximum
```

---

## 🚨 Error Handling

### Common Error Messages

**File Not Found**:
```
Input file not found: missing_file.txt
```

**Cipher Type Mismatch**:
```
Warning: File was encrypted with ultra cipher, but you're using standard cipher.
Use --force to attempt decryption anyway, or use the matching cipher type.
```

**Key Mismatch**:
```
Decryption failed: Key fingerprint mismatch - wrong key or corrupted metadata
```

**Invalid Configuration**:
```
Decryption failed: Rounds must be at least 1
Maximum 100 rounds supported
Unknown profile: invalid_profile
```

### Recovery Options

```bash
# Force decryption despite warnings
python cliopatra.py decrypt-file --force -i file.enc -o output.txt

# Try different cipher type
python cliopatra.py --standard decrypt-file -i file.enc -o output.txt

# Verbose output for debugging
python cliopatra.py --verbose decrypt-file -i file.enc -o output.txt
```

---

## 📊 File Format Details

### Encrypted File Structure

**Text Encryption** (`.json`):
```json
{
  "encrypted_data": "base64-encoded-data",
  "metadata": {
    "version": "faro_cipher_ultra_v1.0",
    "profile": "balanced",
    "rounds": 6,
    "chunk_size": 8192,
    "key_fingerprint": "53136271c432a1af",
    "original_size": 42,
    "cipher_type": "ultra"
  }
}
```

**File Encryption**:
- `filename.enc`: Binary encrypted data
- `filename.enc.meta`: JSON metadata

### Metadata Fields

- `version`: Cipher implementation version
- `profile`: Security profile used
- `rounds`: Number of encryption rounds
- `chunk_size`: Processing chunk size
- `key_fingerprint`: Key verification hash
- `original_size`: Original data size
- `cipher_type`: "standard" or "ultra"
- `chunk_sizes`: Per-chunk sizes (file encryption)

---

## 🔧 Integration Examples

### Bash Scripting

```bash
#!/bin/bash
# Batch file encryption script

KEY_FILE="encryption.key"
INPUT_DIR="documents/"
OUTPUT_DIR="encrypted/"

for file in "$INPUT_DIR"*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Encrypting: $filename"
        python cliopatra.py encrypt-file \
            --key-file "$KEY_FILE" \
            --profile balanced \
            -i "$file" \
            -o "$OUTPUT_DIR$filename.enc"
    fi
done
```

### PowerShell Integration

```powershell
# Windows PowerShell batch encryption
$keyFile = "encryption.key"
$inputDir = "Documents\"
$outputDir = "Encrypted\"

Get-ChildItem $inputDir | ForEach-Object {
    Write-Host "Encrypting: $($_.Name)"
    python cliopatra.py encrypt-file `
        --key-file $keyFile `
        --profile balanced `
        -i $_.FullName `
        -o "$outputDir$($_.Name).enc"
}
```

### Pipeline Processing

```bash
# Encrypt data from pipeline
echo "Secret data" | python cliopatra.py encrypt-text --key "secret" -o encrypted.json

# Decrypt and process
python cliopatra.py decrypt-text --key "secret" -i encrypted.json | grep "pattern"
```

---

## 📈 Performance Guidelines

### File Size Recommendations

| File Size | Recommended Settings |
|-----------|---------------------|
| < 1MB | Default settings |
| 1MB - 100MB | Ultra mode (default), progress enabled |
| 100MB - 1GB | Ultra mode, larger chunk sizes |
| > 1GB | Ultra streaming, progress monitoring |

### Security vs Performance

| Use Case | Profile | Expected Throughput |
|----------|---------|-------------------|
| Non-sensitive data | performance | 80-120 MB/s |
| General use | balanced | 60-90 MB/s |
| Sensitive data | maximum | 30-50 MB/s |

---

**Cliopatra provides professional-grade encryption tooling with ultra-optimized performance, making the Faro Cipher accessible for both research and practical applications.**

**Version**: 1.0.0  
**License**: WTFPL v2  
**Last Updated**: 2024 