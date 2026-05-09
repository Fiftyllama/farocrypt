# Cliopatra — CLI Reference

Cliopatra is the command-line interface for the Faro Cipher.

```
usage: cliopatra.py [-h] [--profile {performance,balanced,maximum}]
                    [--key KEY] [--key-file KEY_FILE] [--rounds ROUNDS]
                    {encrypt-text,decrypt-text,encrypt-file,decrypt-file,info,benchmark}
```

---

## Global options

| Option | Description |
|--------|-------------|
| `--profile`, `-p` | Security profile: `performance`, `balanced` (default), `maximum` |
| `--key`, `-k` | Encryption key as a string. Prompted securely if omitted. |
| `--key-file` | Read the key from a file (binary, whitespace stripped). |
| `--rounds`, `-r` | Override the profile's round count (integer, 1–100). |

---

## Commands

### encrypt-text

Encrypt a string or stdin. Output is hex on stdout, or JSON to a file.

```bash
python cliopatra.py encrypt-text [--text TEXT] [--output FILE]
```

| Option | Description |
|--------|-------------|
| `--text`, `-t` | Text to encrypt. If omitted, reads from stdin until EOF. |
| `--output`, `-o` | Write encrypted JSON to this file instead of printing hex. |

**Examples**

```bash
# Print hex to stdout
python cliopatra.py encrypt-text -k mysecret -t "Hello, world!"

# Save to a file for later decryption
python cliopatra.py encrypt-text -k mysecret -t "Hello" -o hello.json

# Encrypt from stdin
echo "Hello from stdin" | python cliopatra.py encrypt-text -k mysecret -o hello.json
```

---

### decrypt-text

Decrypt a previously encrypted text.

```bash
python cliopatra.py decrypt-text [--input FILE] [--output FILE]
```

| Option | Description |
|--------|-------------|
| `--input`, `-i` | Encrypted JSON file (written by `encrypt-text --output`). If omitted, reads hex from stdin. |
| `--output`, `-o` | Write decrypted text to this file instead of printing. |

**Examples**

```bash
# Decrypt a JSON file
python cliopatra.py decrypt-text -k mysecret -i hello.json

# Save decrypted text to a file
python cliopatra.py decrypt-text -k mysecret -i hello.json -o hello.txt
```

---

### encrypt-file

Encrypt a file. Writes the ciphertext to `--output` and a JSON metadata file to `<output>.meta`. Both files are required for decryption.

```bash
python cliopatra.py encrypt-file --input FILE --output FILE
```

**Examples**

```bash
python cliopatra.py encrypt-file -k mysecret -i document.pdf -o document.enc
# Produces: document.enc and document.enc.meta
```

---

### decrypt-file

Decrypt a file. Reads the ciphertext from `--input` and the metadata from `<input>.meta` (must be in the same directory).

```bash
python cliopatra.py decrypt-file --input FILE --output FILE
```

**Examples**

```bash
python cliopatra.py decrypt-file -k mysecret -i document.enc -o document_restored.pdf
```

---

### info

Show the cipher configuration and full round structure for the given key and profile.

```bash
python cliopatra.py info [-k KEY] [--profile PROFILE]
```

**Example output**

```
Faro Cipher — configuration
========================================
  profile: balanced
  rounds: 6
  key_fingerprint: 3a7f2c1d4e8b9f0a
  ...

Round structure:
   1: in   v2 ×2  +  avalanche_cascade    @ 32KB
   2: out  v0 ×1  +  enhanced_xor         @ 8KB
   ...
```

---

### benchmark

Encrypt and decrypt random data at four sizes (1 KB, 10 KB, 100 KB, 1 MB) and report throughput.

```bash
python cliopatra.py benchmark [-k KEY] [--profile PROFILE]
```

**Example output**

```
Faro Cipher — benchmark
========================================
    1KB  enc=0.012s  dec=0.011s  1.8 MB/s
   10KB  enc=0.021s  dec=0.020s  4.2 MB/s
  100KB  enc=0.087s  dec=0.085s  5.6 MB/s
 1024KB  enc=0.821s  dec=0.815s  6.1 MB/s
```

---

## Key management

Keys can be supplied three ways, in order of preference:

1. `--key-file /path/to/keyfile` — reads the file and strips surrounding whitespace.
2. `--key mysecret` — passed directly on the command line (visible in shell history).
3. Interactive prompt — if neither option is given, the key is read securely with `getpass`.

---

## Metadata files

`encrypt-file` always writes a `.meta` JSON file alongside the ciphertext:

```json
{
  "version": "faro_cipher_v2.0",
  "profile": "balanced",
  "rounds": 6,
  "chunk_size": 65536,
  "key_fingerprint": "3a7f2c1d4e8b9f0a",
  "chunk_sizes": [65536, 65536, 12048]
}
```

Keep both the `.enc` and `.meta` files. Losing the `.meta` file makes decryption impossible.
