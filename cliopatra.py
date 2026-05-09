#!/usr/bin/env python3
"""
Cliopatra — Faro Cipher CLI
============================
Command-line interface for encrypting and decrypting data with the Faro Cipher.

License: WTFPL v2
"""

import argparse
import base64
import json
import os
import sys
import time
import getpass
from pathlib import Path

from faro_cipher import FaroCipher
from faro_cipher.core import EncryptionMetadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_key(args) -> bytes:
    if args.key:
        return args.key.encode('utf-8')
    if args.key_file:
        return Path(args.key_file).read_bytes().strip()
    return getpass.getpass("Enter encryption key: ").encode('utf-8')


def get_cipher(args) -> FaroCipher:
    return FaroCipher(key=get_key(args), profile=args.profile, rounds=args.rounds)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def encrypt_text(args):
    cipher = get_cipher(args)

    if args.text:
        data = args.text.encode('utf-8')
    else:
        print("Enter text to encrypt (Ctrl+D / Ctrl+Z when done):")
        data = sys.stdin.read().encode('utf-8')

    result = cipher.encrypt(data)

    if args.output:
        payload = {
            'encrypted_data': base64.b64encode(result['encrypted_data']).decode('ascii'),
            'metadata': {
                'version':       result['metadata'].version,
                'profile':       result['metadata'].profile,
                'rounds':        result['metadata'].rounds,
                'chunk_size':    result['metadata'].chunk_size,
                'key_fingerprint': result['metadata'].key_fingerprint,
                'original_size': result['metadata'].original_size,
            },
        }
        Path(args.output).write_text(json.dumps(payload, indent=2))
        print(f"Encrypted data saved to: {args.output}")
    else:
        print("Encrypted (hex):")
        print(result['encrypted_data'].hex())
        print(f"\nProfile: {result['metadata'].profile}  "
              f"Rounds: {result['metadata'].rounds}  "
              f"Key: {result['metadata'].key_fingerprint}")


def decrypt_text(args):
    cipher = get_cipher(args)

    if args.input:
        raw = json.loads(Path(args.input).read_text())
        encrypted_data = base64.b64decode(raw['encrypted_data'])
        m = raw['metadata']
        metadata = EncryptionMetadata(
            version=m['version'],
            profile=m['profile'],
            rounds=m['rounds'],
            chunk_size=m['chunk_size'],
            round_structure=[],
            key_fingerprint=m['key_fingerprint'],
            original_size=m.get('original_size'),
        )
    else:
        print("Enter encrypted data (hex):")
        encrypted_data = bytes.fromhex(input().strip())
        rounds = args.rounds or {'performance': 3, 'balanced': 6, 'maximum': 12}[args.profile]
        metadata = EncryptionMetadata(
            version='faro_cipher_v2.0',
            profile=args.profile,
            rounds=rounds,
            chunk_size=65536,
            round_structure=[],
            key_fingerprint="unknown",
            original_size=None,
        )

    try:
        decrypted = cipher.decrypt({'encrypted_data': encrypted_data, 'metadata': metadata})
        text = decrypted.decode('utf-8', errors='replace')
        if args.output:
            Path(args.output).write_text(text)
            print(f"Decrypted text saved to: {args.output}")
        else:
            print("Decrypted text:")
            print(text)
    except Exception as exc:
        print(f"Decryption failed: {exc}")
        sys.exit(1)


def encrypt_file(args):
    if not (args.input and args.output):
        print("Both --input and --output are required for file encryption")
        sys.exit(1)
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    cipher = get_cipher(args)
    size_mb = os.path.getsize(args.input) / (1024 * 1024)
    print(f"Encrypting: {args.input} ({size_mb:.1f} MB) …")

    t0 = time.perf_counter()
    metadata = cipher.encrypt_file(args.input, args.output)
    elapsed = time.perf_counter() - t0

    meta_path = args.output + '.meta'
    meta_dict = {
        'version':       metadata.version,
        'profile':       metadata.profile,
        'rounds':        metadata.rounds,
        'chunk_size':    metadata.chunk_size,
        'key_fingerprint': metadata.key_fingerprint,
        'chunk_sizes':   metadata.chunk_sizes,
    }
    Path(meta_path).write_text(json.dumps(meta_dict, indent=2))

    print(f"Done in {elapsed:.2f}s  ({size_mb / elapsed:.1f} MB/s)")
    print(f"Encrypted: {args.output}")
    print(f"Metadata:  {meta_path}")


def decrypt_file(args):
    if not (args.input and args.output):
        print("Both --input and --output are required for file decryption")
        sys.exit(1)
    if not os.path.exists(args.input):
        print(f"Encrypted file not found: {args.input}")
        sys.exit(1)

    meta_path = args.input + '.meta'
    if not os.path.exists(meta_path):
        print(f"Metadata file not found: {meta_path}")
        sys.exit(1)

    m = json.loads(Path(meta_path).read_text())
    metadata = EncryptionMetadata(
        version=m['version'],
        profile=m['profile'],
        rounds=m['rounds'],
        chunk_size=m['chunk_size'],
        round_structure=[],
        key_fingerprint=m['key_fingerprint'],
        chunk_sizes=m.get('chunk_sizes', []),
    )

    cipher = get_cipher(args)
    print(f"Decrypting: {args.input} …")

    t0 = time.perf_counter()
    ok = cipher.decrypt_file(args.input, args.output, metadata)
    elapsed = time.perf_counter() - t0

    if ok:
        total_mb = sum(metadata.chunk_sizes) / (1024 * 1024)
        print(f"Done in {elapsed:.2f}s  ({total_mb / elapsed:.1f} MB/s)")
        print(f"Decrypted: {args.output}")
    else:
        sys.exit(1)


def show_info(args):
    cipher = get_cipher(args)
    info = cipher.get_info()
    print("Faro Cipher — configuration")
    print("=" * 40)
    for k, v in info.items():
        print(f"  {k}: {v}")
    print("\nRound structure:")
    for i, r in enumerate(cipher.round_structure):
        cs = r['round_chunk_size']
        cs_str = f"{cs // 1024}KB" if cs >= 1024 else f"{cs}B"
        print(f"  {i+1:2d}: {r['shuffle_type']:4s} v{r['shuffle_variant']} ×{r['shuffle_steps']}"
              f"  +  {r['transform_type']:18s}  @ {cs_str}")


def benchmark(args):
    print("Faro Cipher — benchmark")
    print("=" * 40)
    for size in [1024, 10 * 1024, 100 * 1024, 1024 * 1024]:
        label = f"{size // 1024}KB" if size >= 1024 else f"{size}B"
        data = os.urandom(size)
        cipher = get_cipher(args)

        t0 = time.perf_counter()
        enc = cipher.encrypt(data)
        t_enc = time.perf_counter() - t0

        t0 = time.perf_counter()
        dec = cipher.decrypt(enc)
        t_dec = time.perf_counter() - t0

        assert dec == data, f"Round-trip failed for {label}!"
        total = t_enc + t_dec
        mb_s = (size * 2) / (1024 * 1024 * total)
        print(f"  {label:>6}  enc={t_enc:.3f}s  dec={t_dec:.3f}s  {mb_s:.1f} MB/s")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog='cliopatra',
        description="Cliopatra — Faro Cipher CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cliopatra.py encrypt-text -k mysecret -t "Hello, World!"
  python cliopatra.py encrypt-file -k mysecret -i doc.pdf -o doc.enc
  python cliopatra.py decrypt-file -k mysecret -i doc.enc -o doc.pdf
  python cliopatra.py benchmark -k mysecret --profile performance
""",
    )

    # Global options
    parser.add_argument('--profile', '-p', choices=['performance', 'balanced', 'maximum'],
                        default='balanced')
    parser.add_argument('--key', '-k', help='Encryption key (prompted if omitted)')
    parser.add_argument('--key-file', help='File containing the encryption key')
    parser.add_argument('--rounds', '-r', type=int, help='Override round count (1–100)')

    sub = parser.add_subparsers(dest='command')

    # encrypt-text
    p = sub.add_parser('encrypt-text', help='Encrypt text')
    p.add_argument('--text', '-t', help='Text to encrypt')
    p.add_argument('--output', '-o', help='Save encrypted JSON to this file')

    # decrypt-text
    p = sub.add_parser('decrypt-text', help='Decrypt text')
    p.add_argument('--input', '-i', help='Encrypted JSON file')
    p.add_argument('--output', '-o', help='Write decrypted text to this file')

    # encrypt-file
    p = sub.add_parser('encrypt-file', help='Encrypt a file')
    p.add_argument('--input', '-i', required=True)
    p.add_argument('--output', '-o', required=True)

    # decrypt-file
    p = sub.add_parser('decrypt-file', help='Decrypt a file')
    p.add_argument('--input', '-i', required=True)
    p.add_argument('--output', '-o', required=True)

    # info / benchmark
    sub.add_parser('info', help='Show cipher configuration')
    sub.add_parser('benchmark', help='Benchmark encrypt/decrypt speed')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        'encrypt-text': encrypt_text,
        'decrypt-text': decrypt_text,
        'encrypt-file': encrypt_file,
        'decrypt-file': decrypt_file,
        'info':         show_info,
        'benchmark':    benchmark,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    main()
