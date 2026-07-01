# Faro Cipher — Algorithm Specification

## Overview

The Faro Cipher is a symmetric cipher built from two primitives applied in repeated rounds:

- **Faro shuffles** — byte-permutation operations derived from card-shuffling techniques.
- **Self-inverse transforms** — functions that flip selected bytes; applying the same function twice with the same key returns the original data.

The round structure (number of rounds, which shuffle, which transform, how many shuffle steps, which chunk size) is derived deterministically from the encryption key, so the same key always produces the same structure. Decryption applies the same operations in reverse order.

---

## Encryption pipeline

```
Input bytes
    │
    ▼
Pad to multiple of 65536 bytes (max chunk size)
    │
    ▼
For each round r in round_structure:
    │
    ├── Split data into N chunks of size round_structure[r].chunk_size
    │
    ├── For each chunk (in parallel):
    │       ├── Apply transform  (byte-level, key-dependent)
    │       └── Apply shuffle    (byte permutation within chunk, 1–4 steps)
    │
    ├── Shuffle the ORDER of the N chunks
    │       └── Key-derived permutation (seeded from round key material)
    │
    └── Reassemble chunks into a single data block
    │
    ▼
Encrypted bytes
```

### Why chunk-order shuffling produces diffusion

Within a single round, the byte-level shuffle and transform only move bytes *within* their chunk — bytes in chunk 0 never interact with bytes in chunk 1. The chunk-order shuffle fixes this: after all chunks are processed internally, their positions in the output block are permuted. In the next round, a different chunk size is chosen, so boundaries cut across the old chunk boundaries. Bytes that were in separate chunks in round *r* now land in the same chunk in round *r+1*, where the transform and byte-level shuffle can mix them. This cascade of cut-then-mix-at-different-granularities is what creates genuine diffusion across the full data block.

### Chunk-order permutation

For a round with N chunks, the permutation is derived from the round's key material seed:

```python
chunk_rng = np.random.RandomState(round_seed ^ 0xC0FFEE)
permutation = chunk_rng.permutation(N)          # encrypt: apply this order
inverse_perm = np.argsort(permutation)          # decrypt: apply this order
```

The permutation is fully determined by the key and round number, so decryption can reconstruct and invert it without storing additional metadata.

### Decryption

Decryption reverses the order of rounds and, within each round:
1. Reconstruct the chunk-order permutation from round key material.
2. Split the block into N chunks and apply the **inverse permutation** to restore original chunk order.
3. For each chunk: **inverse-shuffle** first, then the same **transform** (transforms are self-inverse).
4. Reassemble.

This is the exact mirror of the encryption pipeline.

---

## Byte-level operations

All operations work directly on bytes (`np.uint8` arrays). This avoids the `np.unpackbits` / `np.packbits` round-trip used in bit-level implementations, saving 8× memory and the corresponding conversion time.

Transforms flip whole bytes with `byte ^= 0xFF` rather than flipping individual bits. The self-inverse property is preserved: `(x ^ 0xFF) ^ 0xFF == x`.

---

## Shuffle operations

Five shuffle types are implemented, each with four variants and a configurable step count (1–4 repetitions per round).

### In-shuffle

Interleaves two halves of the chunk. For a chunk `[a0, a1, ..., ak, b0, b1, ..., bk]`:

```
Variant 0: [a0, b0, a1, b1, ..., ak, bk]   (standard)
Variant 1: [b0, a0, b1, a1, ..., bk, ak]   (halves swapped)
Variant 2: [b0, a0, b1, a1, ...]           (odd positions first)
Variant 3: [a0, b0, a1, b1, ...]           (even positions first)
```

### Out-shuffle

De-interleaves: collects every other element into the two output halves.

```
Variant 0: even-indexed elements → first half,  odd → second half
Variant 1: odd-indexed  elements → first half, even → second half
Variant 2: even positions ← first half, odd positions ← second half (transposed)
Variant 3: reverse of variant 2
```

### Milk shuffle

Alternately takes bytes from the top and bottom of the chunk.

```
Variant 0: top, bottom, top, bottom, ...
Variant 1: bottom, top, bottom, top, ...
Variant 2: bottom, top, ... (starting offset)
Variant 3: top, bottom, ... (starting offset)
```

### Cut shuffle

Moves a 2-byte block from one position to another.

```
Variant 0: cut 2 bytes from top, insert at midpoint
Variant 1: cut 2 bytes from bottom, insert at midpoint
Variant 2: cut 2 bytes from midpoint, move to top
Variant 3: cut 2 bytes from midpoint, move to bottom
```

### None

Identity — no reordering. Four variants all behave identically.

---

## Transform operations

All seven transforms are self-inverse. Each takes a byte array and an integer key, and returns a byte array of the same length.

| Name | Rule (byte i is flipped when…) |
|------|-------------------------------|
| `enhanced_xor` | `(key + i*7) % 256 % 3 == 0` |
| `fibonacci` | position `i` in a Fibonacci-like sequence seeded by key is divisible by 4 |
| `avalanche_cascade` | any of three overlapping key-dependent patterns match |
| `prime_sieve` | `i + (2 + key%97)` passes a simple primality test |
| `invert` | `(i + key) % 3 == 0` |
| `swap_pairs` | swaps bytes at `i` and `i+1` when `(i + key) % 4 == 0` (for even `i`) |
| `bit_flip` | `(i * key) % 7 == 0` |

"Flip" means XOR with `0xFF` (invert all 8 bits of the byte).

---

## Key derivation and round structure generation

### Key material

```python
key_material = hashlib.pbkdf2_hmac(
    'sha256',
    key,
    salt=b'FaroCipherEntropy2024',
    iterations=10000 + rounds * 1000,
    dklen=max(64, rounds * 8),
)
```

A 32-bit master seed is read from `key_material[:4]` and used to seed three independent `numpy.random.RandomState` objects for shuffle selection, transform selection, and parameter selection respectively.

### Round structure

For each round the generator selects:

| Field | Range / choices |
|-------|----------------|
| `shuffle_type` | `none`, `in`, `out`, `milk`, `cut` — distributed evenly, then weighted by least-used |
| `shuffle_variant` | 0–3 |
| `shuffle_steps` | 1–4, weighted by round position |
| `transform_type` | one of the seven transforms — profile emphasis transforms used first, then distributed evenly |
| `transform_key` | 1000–100000, range depends on transform type |
| `round_chunk_size` | power-of-2 value from 2048–65536, selected by position within the round sequence |

### Chunk size strategy

| Round position | Typical range | Purpose |
|----------------|--------------|---------|
| First 3 rounds | 2–8 KB | Local pattern disruption |
| First third | 4–16 KB | Cross-chunk mixing |
| Middle third | 8–32 KB | Maximum diffusion |
| Final third | 2–16 KB | Pattern refinement |
| Last 3 rounds | 4–8 KB | Stable output |

All chunk sizes are powers of 2 and divisors of 65536, so data padded to a multiple of 65536 bytes always divides evenly.

### Key fingerprint

```python
fingerprint = hashlib.md5(key).hexdigest()[:16]
```

Stored in metadata and checked before decryption to detect wrong-key attempts early.

---

## Decryption

1. Verify key fingerprint matches metadata.
2. Apply rounds in reverse order.
3. Within each round:
   a. Reconstruct the chunk-order permutation from round key material.
   b. Split the block into N chunks and apply the **inverse permutation**.
   c. For each chunk: **inverse-shuffle** first, then the same **transform** (self-inverse).
   d. Reassemble chunks into a single block.
4. Trim output to `metadata.original_size`.

---

## Security notes

- The cipher is a research project and has not been formally analysed.
- The PBKDF2 salt is fixed, which means key stretching does not protect against multi-target attacks.
- All transforms flip whole bytes, not individual bits, so the diffusion is coarser than a bit-level implementation.
- Suitable for: learning, experimentation, non-sensitive obfuscation.
- Not suitable for: protecting sensitive data, compliance requirements, production security systems.
