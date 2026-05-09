# Faro Cipher — Performance Notes

## Implementation approach

The cipher works directly on byte arrays (`numpy.uint8`), avoiding the `np.unpackbits` / `np.packbits` conversion that an equivalent bit-level implementation would require. This gives an 8× reduction in array size and eliminates the conversion overhead.

Transforms are implemented as vectorised NumPy operations (boolean index masks + `^= 0xFF`), so no Python-level loops run over individual bytes. The exception is `fibonacci`, which accumulates a recurrence relation and cannot be trivially vectorised — it generates a flip mask with a single Python loop before applying it all at once.

Shuffles are implemented with NumPy slice assignments for `in`, `out`, `cut` (no Python loops at all), and with vectorised index arithmetic for `milk`.

---

## Rough throughput

Figures from a mid-range laptop (Python 3.12, NumPy 1.26). Results will vary with CPU, data size, and which transforms/shuffles happen to be selected for a given key.

| Profile | Rounds | Typical throughput |
|---------|--------|--------------------|
| `performance` | 3 | ~5–10 MB/s |
| `balanced` | 6 | ~2–5 MB/s |
| `maximum` | 12 | ~1–2 MB/s |

Run `python cliopatra.py benchmark -k yourkey` to measure on your own machine.

---

## Where time is spent

### Round count

Throughput scales roughly inversely with round count — doubling rounds halves throughput. This is the dominant factor.

### Chunk size

Each round processes data in its own chunk size (2–64 KB). Larger chunks mean fewer shuffle iterations per round but more data moved per shuffle. The chunk sizes are chosen by the round structure generator and are not user-configurable.

### Transform choice

`prime_sieve` is the slowest transform because it calls a Python-level primality test for each byte position. `fibonacci` is next slowest for the same reason (accumulates state per position). All other transforms are fully vectorised and close to equal in cost.

### Shuffle choice

`milk` is slightly slower than `in` / `out` / `cut` due to the index-arithmetic vectorisation being more complex, but the difference is small compared to the transform cost.

---

## Improving performance

**Choose a lighter profile.** `performance` (3 rounds) is 4× faster than `maximum` (12 rounds) for equivalent data.

**Use a custom round count.** If neither preset fits, pick any value between 1 and 100:

```python
cipher = FaroCipher(key=key, rounds=4)
```

**Use NumPy with a BLAS-linked build.** Install NumPy from a distribution (conda, system package manager) rather than bare `pip install numpy` — you may already have this.

**Parallelize at the file level.** The cipher is single-threaded. If you need to encrypt many files simultaneously, run multiple processes.

---

## Memory usage

Peak memory during encryption of an `n`-byte input is approximately `2n + 65536` bytes: one copy of the working array and one output buffer per round (reused across rounds), plus the 64 KB padding buffer. There is no memory explosion for large files because `encrypt_file` processes one 64 KB block at a time.
