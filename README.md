# Beware, vibecoded slop

# Faro Cipher

A symmetric encryption system built on [Faro card shuffles](https://en.wikipedia.org/wiki/Faro_shuffle) combined with self-inverse byte transforms. Written as a research and learning project.

> **Disclaimer**: This cipher has not undergone formal cryptographic review. It is suitable for learning, experimentation, and non-sensitive data obfuscation — not for protecting secrets that matter.

---

## Installation

```bash
git clone https://github.com/Fiftyllama/farocrypt.git
cd farocrypt
pip install -r requirements.txt
pip install -e .
```

**Requirements**: Python 3.8+, NumPy.

---

## Quick start

```python
from faro_cipher import FaroCipher

cipher = FaroCipher(key=b"my-secret-key", profile="balanced")

# Encrypt
result = cipher.encrypt("Hello, world!")

# Decrypt
plaintext = cipher.decrypt(result)
print(plaintext.decode())   # Hello, world!
```

### File encryption

```python
metadata = cipher.encrypt_file("document.pdf", "document.enc")
cipher.decrypt_file("document.enc", "document_restored.pdf", metadata)
```

---

## Security profiles

| Profile | Rounds | Description |
|---------|--------|-------------|
| `performance` | 3 | Fast, for non-sensitive data |
| `balanced` | 6 | Recommended default |
| `maximum` | 12 | Slower, higher diffusion |

You can also supply a custom round count:

```python
cipher = FaroCipher(key=b"key", rounds=8)
```

---

## CLI — Cliopatra

```bash
# Encrypt text
python cliopatra.py encrypt-text -k mysecret -t "Hello, world!"

# Save encrypted text to a file
python cliopatra.py encrypt-text -k mysecret -t "Hello" -o hello.json

# Decrypt it
python cliopatra.py decrypt-text -k mysecret -i hello.json

# Encrypt / decrypt a file
python cliopatra.py encrypt-file -k mysecret -i doc.pdf -o doc.enc
python cliopatra.py decrypt-file -k mysecret -i doc.enc -o doc.pdf

# Show round structure
python cliopatra.py info -k mysecret

# Benchmark
python cliopatra.py benchmark -k mysecret --profile balanced
```

See [docs/CLI.md](docs/CLI.md) for the full option reference.

---

## How it works

Each encryption round applies two operations to fixed-size chunks of the data:

1. **Transform** — a self-inverse byte-level function (XOR 0xFF on selected bytes). Seven transforms are available: `enhanced_xor`, `fibonacci`, `avalanche_cascade`, `prime_sieve`, `invert`, `swap_pairs`, `bit_flip`.

2. **Shuffle** — a byte-level Faro shuffle rearranges the chunk. Five shuffle types are available (`in`, `out`, `milk`, `cut`, `none`), each with four variants, applied one or more times.

The round structure (which transform, which shuffle, how many steps, which chunk size) is generated deterministically from the key via PBKDF2-HMAC-SHA256. Decryption applies the same operations in reverse order — the transforms are self-inverse, so no separate inverse transform is needed.

See [docs/ALGORITHM.md](docs/ALGORITHM.md) for the full specification.

---

## Project structure

```
farocrypt/
├── faro_cipher/
│   ├── __init__.py      # Public exports
│   ├── core.py          # FaroCipher class and round structure generation
│   ├── shuffles.py      # Byte-level shuffle and inverse-shuffle functions
│   ├── transforms.py    # Self-inverse byte-level transform functions
│   └── utils.py         # Key fingerprinting helpers
├── docs/
│   ├── ALGORITHM.md     # Algorithm specification
│   ├── API.md           # Python API reference
│   ├── CLI.md           # Cliopatra CLI reference
│   └── PERFORMANCE.md   # Performance notes
├── examples/            # Runnable usage examples
├── tests/               # Test suite (unittest)
├── cliopatra.py         # CLI entry point
├── requirements.txt
└── setup.py
```

---

## Running tests

```bash
python -m unittest discover tests/ -v -p "*.py"
```

---

## License

**WTFPL v2** — do whatever you want with this code.
See [LICENSE](LICENSE) or http://www.wtfpl.net/
