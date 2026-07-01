#!/usr/bin/env python3
"""
Faro Cipher — Benchmark & Security Suite
==========================================
Measures speed and cryptographic properties of the cipher. Run this after
making changes to compare results against a baseline.

Usage:
    python tests/benchmark_suite.py              # standard run
    python tests/benchmark_suite.py --large      # add a 1 GB file test
    python tests/benchmark_suite.py --quick      # speed tests only
    python tests/benchmark_suite.py --json out.json   # save results as JSON

Notes:
    - All security metrics use 65536-byte (64 KB) inputs so no padding is added.
      Smaller inputs are padded to 65536 bytes internally, which dominates the
      encrypted output and invalidates distribution tests.
    - Avalanche effect is measured as the fraction of output bits that change
      when one input bit is flipped. The expected value for a strong cipher is
      ~50%. This cipher achieves ~0% because transforms and shuffles operate
      position-by-position (no inter-byte diffusion). That is a known structural
      property, not a bug — see docs/ALGORITHM.md.
    - Key sensitivity measures how much the output changes when one key bit is
      flipped. This is expected to be ~50% and confirms the PBKDF2 round
      structure is working correctly.
"""

import argparse
import json
import os
import random
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from faro_cipher import FaroCipher
from faro_cipher.core import _MAX_CHUNK_SIZE   # 65536

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BENCHMARK_KEY     = b"farocrypt-benchmark-key-2024"
BENCHMARK_PROFILE = "balanced"

# Security tests always use exactly one full chunk (no padding added).
SECURITY_DATA_SIZE = _MAX_CHUNK_SIZE          # 65536 bytes

AVALANCHE_SAMPLES      = 200   # single-bit input flips to average over
KEY_SENSITIVITY_SAMPLES = 100  # single-bit key flips to average over

# Speed test matrix: (label, bytes, use_file_api)
SPEED_TESTS = [
    ("1 KB",   1_024,           False),
    ("10 KB",  10_240,          False),
    ("100 KB", 102_400,         False),
    ("1 MB",   1_048_576,       False),
    ("10 MB",  10_485_760,      True),
    ("100 MB", 104_857_600,     True),
]
LARGE_TEST = ("1 GB", 1_073_741_824, True)

# Round counts checked for the avalanche-vs-rounds table.
ROUND_COUNTS = [1, 2, 3, 6, 9, 12]

# Chi-squared critical value: df=255, p=0.05.
CHI_SQ_CRITICAL = 293.2

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_data(size: int, seed: int = 42) -> bytes:
    """Deterministic pseudo-random bytes."""
    rng = np.random.RandomState(seed)
    return rng.bytes(size)


def flip_bit(data: bytes, bit_index: int) -> bytes:
    """Return data with a single bit flipped."""
    arr = bytearray(data)
    arr[bit_index // 8] ^= 1 << (7 - bit_index % 8)
    return bytes(arr)


def bit_diff_ratio(a: bytes, b: bytes) -> float:
    """Fraction of bits that differ between a and b (up to the shorter length)."""
    length = min(len(a), len(b))
    xa = np.frombuffer(a[:length], dtype=np.uint8)
    xb = np.frombuffer(b[:length], dtype=np.uint8)
    return int(np.unpackbits(xa ^ xb).sum()) / (length * 8)


def byte_diff_ratio(a: bytes, b: bytes) -> float:
    """Fraction of bytes that differ between a and b (up to the shorter length)."""
    length = min(len(a), len(b))
    xa = np.frombuffer(a[:length], dtype=np.uint8)
    xb = np.frombuffer(b[:length], dtype=np.uint8)
    return float(np.sum(xa != xb)) / length

# ---------------------------------------------------------------------------
# Correctness check
# ---------------------------------------------------------------------------

def check_correctness() -> bool:
    """Quick round-trip sanity check across all profiles."""
    ok = True
    for profile in ("performance", "balanced", "maximum"):
        data = make_data(1000, seed=profile.__hash__() & 0xFFFF)
        c = FaroCipher(key=BENCHMARK_KEY, profile=profile)
        try:
            dec = c.decrypt(c.encrypt(data))
            if dec != data:
                print(f"  FAIL  {profile}: round-trip mismatch")
                ok = False
        except Exception as exc:
            print(f"  FAIL  {profile}: {exc}")
            ok = False
    return ok

# ---------------------------------------------------------------------------
# Speed tests
# ---------------------------------------------------------------------------

def run_speed_test(cipher: FaroCipher, size: int, use_file: bool) -> dict:
    """Time one encrypt + decrypt cycle and return the result dict."""
    if use_file:
        with tempfile.TemporaryDirectory() as tmp:
            plain  = os.path.join(tmp, "plain.bin")
            enc    = os.path.join(tmp, "plain.enc")
            dec    = os.path.join(tmp, "plain.dec")

            # Write input file in 1 MB chunks to avoid huge in-memory alloc.
            chunk = make_data(min(size, 1_048_576))
            with open(plain, "wb") as f:
                written = 0
                while written < size:
                    to_write = min(len(chunk), size - written)
                    f.write(chunk[:to_write])
                    written += to_write

            t0  = time.perf_counter()
            meta = cipher.encrypt_file(plain, enc)
            t_enc = time.perf_counter() - t0

            t0  = time.perf_counter()
            ok  = cipher.decrypt_file(enc, dec, meta)
            t_dec = time.perf_counter() - t0

            assert ok, "decrypt_file returned False"
    else:
        data  = make_data(size)
        t0    = time.perf_counter()
        enc   = cipher.encrypt(data)
        t_enc = time.perf_counter() - t0

        t0    = time.perf_counter()
        dec   = cipher.decrypt(enc)
        t_dec = time.perf_counter() - t0

        assert dec == data, "in-memory round-trip mismatch"

    mb = size / 1_048_576
    return {
        "size_bytes":  size,
        "enc_time_s":  t_enc,
        "dec_time_s":  t_dec,
        "enc_mb_s":    mb / t_enc,
        "dec_mb_s":    mb / t_dec,
    }

# ---------------------------------------------------------------------------
# Byte distribution
# ---------------------------------------------------------------------------

def measure_byte_distribution(cipher: FaroCipher) -> dict:
    """
    Chi-squared uniformity test and Shannon entropy on encrypted output.
    Uses exactly SECURITY_DATA_SIZE bytes so no padding is added.
    """
    data  = make_data(SECURITY_DATA_SIZE)
    enc   = cipher.encrypt(data)["encrypted_data"]
    arr   = np.frombuffer(enc, dtype=np.uint8)

    counts   = np.bincount(arr, minlength=256).astype(float)
    expected = len(arr) / 256.0
    chi_sq   = float(np.sum((counts - expected) ** 2 / expected))

    probs   = counts[counts > 0] / len(arr)
    entropy = float(-np.sum(probs * np.log2(probs)))

    return {
        "entropy_bits_per_byte": entropy,
        "chi_squared":           chi_sq,
        "chi_sq_critical":       CHI_SQ_CRITICAL,
        "chi_sq_pass":           chi_sq < CHI_SQ_CRITICAL,
        "byte_count_min":        int(counts.min()),
        "byte_count_max":        int(counts.max()),
        "byte_count_expected":   expected,
    }

# ---------------------------------------------------------------------------
# Avalanche effect
# ---------------------------------------------------------------------------

def measure_avalanche(cipher: FaroCipher, samples: int = AVALANCHE_SAMPLES) -> dict:
    """
    Flip SAMPLES randomly chosen input bits one at a time and measure how
    many bits change in the corresponding output.

    For a cipher with full diffusion the expected result is ~50%.
    This cipher achieves ~0% because each output bit depends on only one input
    bit — the shuffles permute positions and the transforms conditionally invert
    bytes, but neither operation mixes information between bytes.
    """
    data     = make_data(SECURITY_DATA_SIZE)
    baseline = cipher.encrypt(data)["encrypted_data"]

    n_bits  = len(data) * 8
    rng     = random.Random(7331)
    bit_pos = rng.sample(range(n_bits), min(samples, n_bits))

    bit_ratios  = []
    byte_ratios = []

    for pos in bit_pos:
        modified = flip_bit(data, pos)
        output   = cipher.encrypt(modified)["encrypted_data"]
        bit_ratios.append(bit_diff_ratio(baseline, output))
        byte_ratios.append(byte_diff_ratio(baseline, output))

    return {
        "bit_avalanche_mean":  float(np.mean(bit_ratios)),
        "bit_avalanche_std":   float(np.std(bit_ratios)),
        "byte_avalanche_mean": float(np.mean(byte_ratios)),
        "byte_avalanche_std":  float(np.std(byte_ratios)),
        "samples":             len(bit_pos),
    }

# ---------------------------------------------------------------------------
# Key sensitivity
# ---------------------------------------------------------------------------

def measure_key_sensitivity(samples: int = KEY_SENSITIVITY_SAMPLES) -> dict:
    """
    Flip SAMPLES randomly chosen key bits one at a time and measure how many
    output bits change relative to the baseline key.

    Expected ~50% because a 1-bit key change re-derives the entire round
    structure via PBKDF2, producing a completely different permutation.
    """
    data     = make_data(SECURITY_DATA_SIZE)
    baseline = FaroCipher(key=BENCHMARK_KEY, profile=BENCHMARK_PROFILE) \
                   .encrypt(data)["encrypted_data"]

    n_bits  = len(BENCHMARK_KEY) * 8
    rng     = random.Random(1337)
    bit_pos = rng.sample(range(n_bits), min(samples, n_bits))

    bit_ratios  = []
    byte_ratios = []

    for pos in bit_pos:
        mod_key = flip_bit(BENCHMARK_KEY, pos)
        output  = FaroCipher(key=mod_key, profile=BENCHMARK_PROFILE) \
                      .encrypt(data)["encrypted_data"]
        bit_ratios.append(bit_diff_ratio(baseline, output))
        byte_ratios.append(byte_diff_ratio(baseline, output))

    return {
        "bit_sensitivity_mean":  float(np.mean(bit_ratios)),
        "bit_sensitivity_std":   float(np.std(bit_ratios)),
        "byte_sensitivity_mean": float(np.mean(byte_ratios)),
        "byte_sensitivity_std":  float(np.std(byte_ratios)),
        "samples":               len(bit_pos),
    }

# ---------------------------------------------------------------------------
# Avalanche vs round count
# ---------------------------------------------------------------------------

def measure_round_contribution() -> list:
    """
    Measure bit-level avalanche for each entry in ROUND_COUNTS.
    Shows how (or whether) diffusion accumulates with more rounds.

    Note: round structures differ across counts (PBKDF2 output length varies),
    so this is not a pure "add one round" comparison.
    """
    data    = make_data(SECURITY_DATA_SIZE)
    results = []

    for n in ROUND_COUNTS:
        cipher = FaroCipher(key=BENCHMARK_KEY, profile=BENCHMARK_PROFILE, rounds=n)
        avl    = measure_avalanche(cipher, samples=50)
        ks     = measure_key_sensitivity(samples=30)
        results.append({
            "rounds":             n,
            "bit_avalanche":      avl["bit_avalanche_mean"],
            "byte_avalanche":     avl["byte_avalanche_mean"],
            "bit_key_sensitivity": ks["bit_sensitivity_mean"],
        })

    return results

# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

W = 66
SEP    = "=" * W
SUBSEP = "-" * W


def _pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def _rating(v: float, ideal: float, warn_margin: float = 0.10) -> str:
    """Return GOOD / WARN / NOTE depending on distance from ideal."""
    if abs(v - ideal) <= warn_margin * ideal:
        return "GOOD"
    if abs(v - ideal) <= 0.25 * ideal:
        return "WARN"
    return "NOTE"


def print_header():
    print(SEP)
    print("FARO CIPHER — BENCHMARK & SECURITY SUITE".center(W))
    print(SEP)
    c = FaroCipher(key=BENCHMARK_KEY, profile=BENCHMARK_PROFILE)
    print(f"  Profile       : {BENCHMARK_PROFILE}")
    print(f"  Key fingerprint: {c.key_fingerprint}")
    print(f"  Security data size: {SECURITY_DATA_SIZE // 1024} KB (one full chunk, no padding)")
    print()


def print_speed_results(results: list):
    print(SEP)
    print("SPEED")
    print(SEP)
    print(f"  {'Size':>8}  {'Enc (s)':>9}  {'Dec (s)':>9}  {'Enc MB/s':>10}  {'Dec MB/s':>10}")
    print(f"  {SUBSEP}")
    for label, r in results:
        print(
            f"  {label:>8}  "
            f"{r['enc_time_s']:9.3f}  "
            f"{r['dec_time_s']:9.3f}  "
            f"{r['enc_mb_s']:10.2f}  "
            f"{r['dec_mb_s']:10.2f}"
        )
    print()


def print_distribution_results(d: dict):
    print(SEP)
    print("BYTE DISTRIBUTION  (input: 64 KB random data, no padding)")
    print(SEP)
    entropy_rating = "GOOD" if d["entropy_bits_per_byte"] >= 7.9 else (
                     "WARN" if d["entropy_bits_per_byte"] >= 7.5 else "NOTE")
    chi_rating     = "GOOD" if d["chi_sq_pass"] else "NOTE"
    print(f"  Shannon entropy : {d['entropy_bits_per_byte']:.4f} bits/byte  "
          f"(ideal 8.0)  [{entropy_rating}]")
    print(f"  Chi-squared     : {d['chi_squared']:.1f}  "
          f"(critical {d['chi_sq_critical']:.1f}, p=0.05, df=255)  [{chi_rating}]")
    print(f"  Byte counts     : min={d['byte_count_min']}  "
          f"max={d['byte_count_max']}  expected={d['byte_count_expected']:.1f}")
    print()


def print_avalanche_results(a: dict):
    print(SEP)
    print("AVALANCHE EFFECT  (single-bit input flip, 64 KB data)")
    print(SEP)
    bit_r  = _rating(a["bit_avalanche_mean"],  0.50)
    byte_r = _rating(a["byte_avalanche_mean"], 0.50)
    print(f"  Bit-level  : {_pct(a['bit_avalanche_mean'])} "
          f"(±{_pct(a['bit_avalanche_std'])})  [{bit_r}]")
    print(f"  Byte-level : {_pct(a['byte_avalanche_mean'])} "
          f"(±{_pct(a['byte_avalanche_std'])})  [{byte_r}]")
    print(f"  Samples    : {a['samples']} random single-bit input flips")
    print()
    print("  Context: this cipher achieves ~0% because transforms operate")
    print("  position-by-position with no inter-byte mixing. A 1-bit input")
    print("  change moves to a different position but never fans out. Compare")
    print("  key sensitivity below — that IS close to 50%.")
    print()


def print_key_sensitivity_results(k: dict):
    print(SEP)
    print("KEY SENSITIVITY  (single-bit key flip, same 64 KB plaintext)")
    print(SEP)
    bit_r  = _rating(k["bit_sensitivity_mean"],  0.50)
    byte_r = _rating(k["byte_sensitivity_mean"], 1.00, warn_margin=0.05)
    print(f"  Bit-level  : {_pct(k['bit_sensitivity_mean'])} "
          f"(±{_pct(k['bit_sensitivity_std'])})  [{bit_r}]")
    print(f"  Byte-level : {_pct(k['byte_sensitivity_mean'])} "
          f"(±{_pct(k['byte_sensitivity_std'])})  [{byte_r}]")
    print(f"  Samples    : {k['samples']} random single-bit key flips")
    print()


def print_round_contribution(rows: list):
    print(SEP)
    print("DIFFUSION vs ROUND COUNT")
    print(SEP)
    print(f"  {'Rounds':>7}  {'Bit avalanche':>14}  {'Byte avalanche':>15}  {'Key sensitivity':>16}")
    print(f"  {SUBSEP}")
    for r in rows:
        print(
            f"  {r['rounds']:>7}  "
            f"{_pct(r['bit_avalanche']):>14}  "
            f"{_pct(r['byte_avalanche']):>15}  "
            f"{_pct(r['bit_key_sensitivity']):>16}"
        )
    print()
    print("  Note: round structures differ across counts (PBKDF2 length varies),")
    print("  so this is not a pure 'one extra round' comparison.")
    print()


def print_summary(all_results: dict):
    print(SEP)
    print("SUMMARY")
    print(SEP)
    checks = []
    d = all_results.get("distribution", {})
    if d:
        checks.append(("Byte entropy >= 7.9",
                        d["entropy_bits_per_byte"] >= 7.9,
                        f"{d['entropy_bits_per_byte']:.4f}"))
        checks.append(("Chi-squared < 293 (uniform output)",
                        d["chi_sq_pass"],
                        f"{d['chi_squared']:.1f}"))

    k = all_results.get("key_sensitivity", {})
    if k:
        checks.append(("Key sensitivity (bit) in [40%, 60%]",
                        0.40 <= k["bit_sensitivity_mean"] <= 0.60,
                        _pct(k["bit_sensitivity_mean"])))
        checks.append(("Key sensitivity (byte) > 80%",
                        k["byte_sensitivity_mean"] > 0.80,
                        _pct(k["byte_sensitivity_mean"])))

    for label, passed, value in checks:
        tag = "PASS" if passed else "FAIL"
        print(f"  [{tag}]  {label}  ({value})")
    print()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Faro Cipher benchmark and security suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--large", action="store_true",
                        help="Include a 1 GB file test (needs ~2 GB free disk space)")
    parser.add_argument("--quick", action="store_true",
                        help="Speed tests only; skip security analysis")
    parser.add_argument("--json", metavar="FILE",
                        help="Write all numeric results to a JSON file")
    args = parser.parse_args()

    print_header()
    all_results = {}

    # --- Correctness ---
    print("Correctness check... ", end="", flush=True)
    if not check_correctness():
        print("\nAborted: cipher failed round-trip test.")
        sys.exit(1)
    print("OK")
    print()

    # --- Speed ---
    print("Running speed tests...")
    cipher = FaroCipher(key=BENCHMARK_KEY, profile=BENCHMARK_PROFILE)
    speed_rows = []
    tests = SPEED_TESTS + ([LARGE_TEST] if args.large else [])
    for label, size, use_file in tests:
        print(f"  {label}... ", end="", flush=True)
        try:
            r = run_speed_test(cipher, size, use_file)
            speed_rows.append((label, r))
            print(f"enc {r['enc_mb_s']:.2f} MB/s  dec {r['dec_mb_s']:.2f} MB/s")
        except Exception as exc:
            print(f"FAILED: {exc}")
    all_results["speed"] = {label: r for label, r in speed_rows}

    print()
    print_speed_results(speed_rows)

    if args.quick:
        if args.json:
            Path(args.json).write_text(json.dumps(all_results, indent=2))
            print(f"Results saved to {args.json}")
        return

    # --- Security ---
    print("Running security tests (using 64 KB data, no padding)...")
    cipher = FaroCipher(key=BENCHMARK_KEY, profile=BENCHMARK_PROFILE)

    print("  Byte distribution... ", end="", flush=True)
    dist = measure_byte_distribution(cipher)
    print(f"entropy={dist['entropy_bits_per_byte']:.4f}  chi_sq={dist['chi_squared']:.1f}")
    all_results["distribution"] = dist

    print(f"  Avalanche ({AVALANCHE_SAMPLES} samples)... ", end="", flush=True)
    avl = measure_avalanche(cipher)
    print(f"bit={_pct(avl['bit_avalanche_mean'])}  byte={_pct(avl['byte_avalanche_mean'])}")
    all_results["avalanche"] = avl

    print(f"  Key sensitivity ({KEY_SENSITIVITY_SAMPLES} samples)... ", end="", flush=True)
    ks = measure_key_sensitivity()
    print(f"bit={_pct(ks['bit_sensitivity_mean'])}  byte={_pct(ks['byte_sensitivity_mean'])}")
    all_results["key_sensitivity"] = ks

    print("  Round contribution... ", end="", flush=True)
    rc = measure_round_contribution()
    print("done")
    all_results["round_contribution"] = rc

    print()

    # --- Full report ---
    print_distribution_results(dist)
    print_avalanche_results(avl)
    print_key_sensitivity_results(ks)
    print_round_contribution(rc)
    print_summary(all_results)

    if args.json:
        Path(args.json).write_text(json.dumps(all_results, indent=2))
        print(f"Results saved to {args.json}")

    print(SEP)


if __name__ == "__main__":
    main()
