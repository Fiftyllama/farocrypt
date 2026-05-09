# Faro Cipher — Python API Reference

## Package imports

```python
from faro_cipher import FaroCipher, EncryptionMetadata, SecurityProfile
from faro_cipher import generate_key_fingerprint, verify_key_compatibility
```

---

## FaroCipher

`faro_cipher.core.FaroCipher`

The single cipher class. Constructs a deterministic round structure from the supplied key and provides encrypt/decrypt for both in-memory data and files.

### Constructor

```python
FaroCipher(
    key: bytes,
    profile: str = "balanced",
    rounds: int | None = None,
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `bytes` | Encryption key (any length). |
| `profile` | `str` | `"performance"`, `"balanced"` (default), or `"maximum"`. |
| `rounds` | `int \| None` | Override the profile's round count (1–100). Sets `profile` to `"custom-N"`. |

Raises `ValueError` for unknown profiles or out-of-range round counts.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `profile` | `str` | Active profile name. |
| `rounds` | `int` | Number of encryption rounds. |
| `key_fingerprint` | `str` | 16-character hex fingerprint of the key. |
| `round_structure` | `list[dict]` | Full round configuration (see below). |
| `chunk_size` | `int` | Always `65536` — the maximum chunk size used internally. |

Each entry in `round_structure` contains:

```python
{
    'shuffle_type':     str,   # 'none' | 'in' | 'out' | 'milk' | 'cut'
    'shuffle_variant':  int,   # 0–3
    'shuffle_steps':    int,   # 1–4
    'transform_type':   str,   # one of the seven transform names
    'transform_key':    int,   # derived from key material
    'round_chunk_size': int,   # power-of-2 chunk size for this round
}
```

---

### `encrypt(data)`

```python
result = cipher.encrypt(data: bytes | str) -> dict
```

Returns a dictionary:

```python
{
    'encrypted_data': bytes,
    'metadata':       EncryptionMetadata,
}
```

String input is UTF-8 encoded automatically. The encrypted bytes are always longer than the input (padded to a multiple of 65536 bytes); `metadata.original_size` records the true input length for trimming on decryption.

### `decrypt(encrypted_result)`

```python
plaintext = cipher.decrypt(encrypted_result: dict) -> bytes
```

Accepts the dict returned by `encrypt()`. Raises `ValueError` if the key fingerprint does not match the metadata.

---

### `encrypt_file(input_path, output_path)`

```python
metadata = cipher.encrypt_file(input_path: str, output_path: str) -> EncryptionMetadata
```

Reads `input_path` in 65536-byte blocks, encrypts each block, and writes the result to `output_path`. Each block is preceded by a 4-byte big-endian length header.

Returns `EncryptionMetadata` — **save this**; it is required for decryption.

### `decrypt_file(input_path, output_path, metadata)`

```python
ok = cipher.decrypt_file(
    input_path: str,
    output_path: str,
    metadata: EncryptionMetadata,
) -> bool
```

Returns `True` on success, `False` on failure (also prints an error message).

---

### `get_info()`

```python
info = cipher.get_info() -> dict
```

Returns a summary dict:

```python
{
    'profile':                   str,
    'description':               str,
    'rounds':                    int,
    'chunk_size':                int,
    'key_fingerprint':           str,
    'shuffle_types_available':   list[str],
    'transforms_available':      list[str],
}
```

---

## EncryptionMetadata

`faro_cipher.core.EncryptionMetadata` (dataclass)

Holds everything needed to decrypt a ciphertext. You are responsible for persisting this alongside the encrypted data.

```python
@dataclass
class EncryptionMetadata:
    version:         str
    profile:         str
    rounds:          int
    chunk_size:      int
    round_structure: list[dict]     # empty [] when loaded from JSON
    key_fingerprint: str
    original_size:   int | None     # set for in-memory encrypt()
    chunk_sizes:     list[int] | None  # set for encrypt_file()
```

When serialising to JSON for file encryption, the round structure is not stored (it is regenerated from the key). Store at minimum: `version`, `profile`, `rounds`, `chunk_size`, `key_fingerprint`, `chunk_sizes`.

---

## SecurityProfile

`faro_cipher.core.SecurityProfile`

Access the preset configurations:

```python
SecurityProfile.get("performance")  # -> dict
SecurityProfile.get("balanced")
SecurityProfile.get("maximum")
```

Each dict contains `rounds`, `emphasis` (list of transform names emphasised in early rounds), and `description`.

---

## Utility functions

### `generate_key_fingerprint(key)`

```python
fingerprint = generate_key_fingerprint(key: bytes) -> str
```

Returns the first 16 hex characters of `md5(key)`. Used internally by `FaroCipher`.

### `verify_key_compatibility(key, fingerprint)`

```python
ok = verify_key_compatibility(key: bytes, fingerprint: str) -> bool
```

Returns `True` if `generate_key_fingerprint(key) == fingerprint`.

---

## Examples

### In-memory round-trip

```python
from faro_cipher import FaroCipher

cipher = FaroCipher(key=b"secret", profile="balanced")

result    = cipher.encrypt(b"Hello, world!")
plaintext = cipher.decrypt(result)

assert plaintext == b"Hello, world!"
```

### File encryption with JSON metadata

```python
import json
from faro_cipher import FaroCipher
from faro_cipher.core import EncryptionMetadata

cipher = FaroCipher(key=b"secret", profile="balanced")

# Encrypt
metadata = cipher.encrypt_file("report.pdf", "report.enc")

meta_dict = {
    "version":         metadata.version,
    "profile":         metadata.profile,
    "rounds":          metadata.rounds,
    "chunk_size":      metadata.chunk_size,
    "key_fingerprint": metadata.key_fingerprint,
    "chunk_sizes":     metadata.chunk_sizes,
}
with open("report.enc.meta", "w") as f:
    json.dump(meta_dict, f)

# Decrypt (later, possibly in a different process)
with open("report.enc.meta") as f:
    m = json.load(f)

meta = EncryptionMetadata(
    version=m["version"],
    profile=m["profile"],
    rounds=m["rounds"],
    chunk_size=m["chunk_size"],
    round_structure=[],
    key_fingerprint=m["key_fingerprint"],
    chunk_sizes=m["chunk_sizes"],
)

ok = cipher.decrypt_file("report.enc", "report_restored.pdf", meta)
assert ok
```

### Custom round count

```python
cipher = FaroCipher(key=b"secret", rounds=9)
# cipher.profile == "custom-9"
```

### Error handling

```python
from faro_cipher import FaroCipher

cipher_a = FaroCipher(key=b"correct-key", profile="balanced")
cipher_b = FaroCipher(key=b"wrong-key",   profile="balanced")

result = cipher_a.encrypt(b"sensitive data")

try:
    cipher_b.decrypt(result)          # raises ValueError
except ValueError as exc:
    print(exc)                        # Key fingerprint mismatch
```
