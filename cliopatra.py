#!/usr/bin/env python3
"""
Cliopatra - Faro Cipher CLI Utility
===================================

Command-line interface for encrypting and decrypting data using the Faro Cipher.
Named after the legendary queen who mastered the art of codes and ciphers.

Now powered by Ultra-optimized algorithmic improvements for maximum performance!

License: WTFPL v2 - Do whatever you want with this code.
SPDX-License-Identifier: WTFPL
"""

import argparse
import sys
import os
import getpass
import json
from pathlib import Path
from faro_cipher import FaroCipher, UltraFaroCipher

def get_cipher(args):
    """Get the appropriate cipher implementation"""
    key = get_key(args)
    
    if args.standard:
        return FaroCipher(key=key, profile=args.profile, rounds=args.rounds)
    else:
        # Use Ultra by default for maximum performance
        cache_opt = not args.no_cache if hasattr(args, 'no_cache') else True
        return UltraFaroCipher(key=key, profile=args.profile, rounds=args.rounds, cache_optimize=cache_opt)

def get_key(args):
    """Get encryption key from various sources"""
    if args.key:
        return args.key.encode('utf-8')
    elif args.key_file:
        with open(args.key_file, 'rb') as f:
            return f.read().strip()
    else:
        # Prompt for key securely
        key = getpass.getpass("Enter encryption key: ")
        return key.encode('utf-8')

def encrypt_text(args):
    """Encrypt text data"""
    cipher = get_cipher(args)
    
    # Get input text
    if args.text:
        data = args.text.encode('utf-8')
    else:
        print("Enter text to encrypt (Ctrl+D when done):")
        data = sys.stdin.read().encode('utf-8')
    
    # Encrypt
    print(f"Encrypting with {'Standard' if args.standard else 'Ultra'} cipher...")
    result = cipher.encrypt(data)
    
    # Output
    if args.output:
        # Save as JSON metadata + base64 data
        import base64
        output_data = {
            'encrypted_data': base64.b64encode(result['encrypted_data']).decode('ascii'),
            'metadata': {
                'version': result['metadata'].version,
                'profile': result['metadata'].profile,
                'rounds': result['metadata'].rounds,
                'chunk_size': result['metadata'].chunk_size,
                'key_fingerprint': result['metadata'].key_fingerprint,
                'original_size': result['metadata'].original_size,
                'cipher_type': 'standard' if args.standard else 'ultra'
            }
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Encrypted data saved to: {args.output}")
    else:
        # Output as hex
        print("Encrypted data (hex):")
        print(result['encrypted_data'].hex())
        print(f"\nMetadata:")
        print(f"  Profile: {result['metadata'].profile}")
        print(f"  Rounds: {result['metadata'].rounds}")
        print(f"  Key fingerprint: {result['metadata'].key_fingerprint}")
        print(f"  Cipher: {'Standard' if args.standard else 'Ultra'}")

def decrypt_text(args):
    """Decrypt text data"""
    cipher = get_cipher(args)
    
    # Get encrypted data
    if args.input:
        # Load from JSON file
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        import base64
        encrypted_data = base64.b64decode(data['encrypted_data'])
        
        # Check cipher type compatibility
        stored_cipher_type = data['metadata'].get('cipher_type', 'standard')
        current_cipher_type = 'standard' if args.standard else 'ultra'
        
        if stored_cipher_type != current_cipher_type and not args.force:
            print(f"Warning: File was encrypted with {stored_cipher_type} cipher, "
                  f"but you're using {current_cipher_type} cipher.")
            print("   Use --force to attempt decryption anyway, or use the matching cipher type.")
            sys.exit(1)
        
        # Reconstruct metadata
        from faro_cipher.core import EncryptionMetadata
        metadata = EncryptionMetadata(
            version=data['metadata']['version'],
            profile=data['metadata']['profile'],
            rounds=data['metadata']['rounds'],
            chunk_size=data['metadata']['chunk_size'],
            round_structure=[],  # Will be regenerated
            key_fingerprint=data['metadata']['key_fingerprint'],
            original_size=data['metadata']['original_size']
        )
        
        result = {'encrypted_data': encrypted_data, 'metadata': metadata}
    else:
        print("Enter encrypted data (hex format):")
        hex_data = input().strip()
        encrypted_data = bytes.fromhex(hex_data)
        
        # For direct hex input, we need to reconstruct metadata
        print("⚠️  Warning: Minimal metadata available for hex input")
        from faro_cipher.core import EncryptionMetadata
        rounds = args.rounds if args.rounds else (3 if args.profile == "performance" else (6 if args.profile == "balanced" else 12))
        metadata = EncryptionMetadata(
            version='faro_cipher_ultra_v1.0' if not args.standard else 'faro_cipher_v1.0',
            profile=args.profile,
            rounds=rounds,
            chunk_size=8192,
            round_structure=[],
            key_fingerprint="unknown",
            original_size=None
        )
        
        result = {'encrypted_data': encrypted_data, 'metadata': metadata}
    
    # Decrypt
    try:
        print(f"Decrypting with {'Standard' if args.standard else 'Ultra'} cipher...")
        decrypted_data = cipher.decrypt(result)
        decrypted_text = decrypted_data.decode('utf-8', errors='replace')
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(decrypted_text)
            print(f"Decrypted text saved to: {args.output}")
        else:
            print("Decrypted text:")
            print(decrypted_text)
            
    except Exception as e:
        print(f"Decryption failed: {e}")
        if not args.force:
            print("   Try using --force or the correct cipher type (--standard)")
        sys.exit(1)

def encrypt_file(args):
    """Encrypt a file"""
    if not args.input or not args.output:
        print("Both input and output files required for file encryption")
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(1)
    
    cipher = get_cipher(args)
    
    try:
        file_size = os.path.getsize(args.input)
        size_mb = file_size / (1024 * 1024)
        
        print(f"Encrypting file with {'Standard' if args.standard else 'Ultra'} cipher: {args.input} ({size_mb:.1f}MB)")
        
        if hasattr(cipher, 'encrypt_file_ultra') and not args.standard:
            # Use ultra streaming encryption for large files
            print("   Using ultra streaming encryption for optimal performance...")
            metadata = cipher.encrypt_file_ultra(args.input, args.output, progress=True)
        else:
            # Use standard file encryption
            metadata = cipher.encrypt_file(args.input, args.output)
        
        # Save metadata
        metadata_file = args.output + '.meta'
        metadata_dict = {
            'version': metadata.version,
            'profile': metadata.profile,
            'rounds': metadata.rounds,
            'chunk_size': metadata.chunk_size,
            'key_fingerprint': metadata.key_fingerprint,
            'cipher_type': 'standard' if args.standard else 'ultra'
        }
        
        # Add chunk sizes if available
        if hasattr(metadata, 'chunk_sizes') and metadata.chunk_sizes:
            metadata_dict['chunk_sizes'] = metadata.chunk_sizes
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
        
        print(f"File encrypted successfully!")
        print(f"   Encrypted file: {args.output}")
        print(f"   Metadata file: {metadata_file}")
        print(f"   Profile: {metadata.profile} ({metadata.rounds} rounds)")
        print(f"   Cipher: {'Standard' if args.standard else 'Ultra'}")
        
    except Exception as e:
        print(f"Encryption failed: {e}")
        sys.exit(1)

def decrypt_file(args):
    """Decrypt a file"""
    if not args.input or not args.output:
        print("Both input and output files required for file decryption")
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"Encrypted file not found: {args.input}")
        sys.exit(1)
    
    # Load metadata
    metadata_file = args.input + '.meta'
    if not os.path.exists(metadata_file):
        print(f"Metadata file not found: {metadata_file}")
        sys.exit(1)
    
    with open(metadata_file, 'r') as f:
        metadata_dict = json.load(f)
    
    # Check cipher type compatibility
    stored_cipher_type = metadata_dict.get('cipher_type', 'standard')
    current_cipher_type = 'standard' if args.standard else 'ultra'
    
    if stored_cipher_type != current_cipher_type and not args.force:
        print(f"Warning: File was encrypted with {stored_cipher_type} cipher, "
              f"but you're using {current_cipher_type} cipher.")
        print("   Use --force to attempt decryption anyway, or use --standard for standard cipher.")
        sys.exit(1)
    
    from faro_cipher.core import EncryptionMetadata
    metadata = EncryptionMetadata(
        version=metadata_dict['version'],
        profile=metadata_dict['profile'],
        rounds=metadata_dict['rounds'],
        chunk_size=metadata_dict['chunk_size'],
        round_structure=[],  # Will be regenerated
        key_fingerprint=metadata_dict['key_fingerprint'],
        chunk_sizes=metadata_dict.get('chunk_sizes', [])
    )
    
    cipher = get_cipher(args)
    
    try:
        print(f"Decrypting file with {'Standard' if args.standard else 'Ultra'} cipher: {args.input}")
        
        if hasattr(cipher, 'decrypt_file_ultra') and stored_cipher_type == 'ultra' and not args.standard:
            # Use ultra streaming decryption
            print("   Using ultra streaming decryption...")
            success = cipher.decrypt_file_ultra(args.input, args.output, metadata)
        else:
            # Use standard file decryption
            success = cipher.decrypt_file(args.input, args.output, metadata)
        
        if success:
            print(f"File decrypted successfully!")
            print(f"   Decrypted file: {args.output}")
            print(f"   Profile: {metadata.profile} ({metadata.rounds} rounds)")
        else:
            print("Decryption failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Decryption failed: {e}")
        if not args.force:
            print("   Try using --force or the correct cipher type")
        sys.exit(1)

def show_info(args):
    """Show cipher information"""
    cipher = get_cipher(args)
    info = cipher.get_info() if hasattr(cipher, 'get_info') else {}
    
    print("Cliopatra - Faro Cipher Information")
    print("=" * 40)
    print(f"Implementation: {'Standard' if args.standard else 'Ultra-Optimized'}")
    
    if hasattr(cipher, 'get_optimization_info') and not args.standard:
        opt_info = cipher.get_optimization_info()
        print(f"Version: {opt_info['version']}")
        print(f"Optimizations:")
        for opt in opt_info['optimizations']:
            print(f"  • {opt}")
        print(f"Expected speedup: {opt_info['expected_speedup']}")
        print(f"Memory efficiency: {opt_info['memory_efficiency']}")
    
    if info:
        print(f"Profile: {info['profile']}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Rounds: {info['rounds']}")
        print(f"Chunk size: {info['chunk_size']} bytes")
        print(f"Key fingerprint: {info['key_fingerprint']}")
    
    # Show entropy information if available
    if hasattr(cipher, 'round_structure') and cipher.round_structure:
        print(f"\nRound Structure:")
        for i, round_info in enumerate(cipher.round_structure):
            entropy_str = f" (entropy: {round_info.get('entropy_score', 0):.1f})" if 'entropy_score' in round_info else ""
            chunk_size = round_info.get('round_chunk_size', 8192)
            chunk_str = f"{chunk_size//1024}KB" if chunk_size >= 1024 else f"{chunk_size}B"
            print(f"  Round {i+1}: {round_info['shuffle_type']} + {round_info['transform_type']} "
                  f"@ {chunk_str}{entropy_str}")

def benchmark_cipher(args):
    """Benchmark cipher performance"""
    print("Cliopatra Performance Benchmark")
    print("=" * 40)
    
    # Test different data sizes
    test_sizes = [1024, 10*1024, 100*1024, 1024*1024]  # 1KB, 10KB, 100KB, 1MB
    
    for size in test_sizes:
        size_label = f"{size//1024}KB" if size >= 1024 else f"{size}B"
        print(f"\nTesting {size_label}:")
        
        test_data = os.urandom(size)
        
        if not args.standard:
            # Test Ultra
            print("  Ultra Cipher:")
            ultra_cipher = UltraFaroCipher(key=get_key(args), profile=args.profile, rounds=args.rounds)
            
            import time
            start = time.perf_counter()
            ultra_encrypted = ultra_cipher.encrypt(test_data)
            ultra_encrypt_time = time.perf_counter() - start
            
            start = time.perf_counter()
            ultra_decrypted = ultra_cipher.decrypt(ultra_encrypted)
            ultra_decrypt_time = time.perf_counter() - start
            
            ultra_total = ultra_encrypt_time + ultra_decrypt_time
            ultra_throughput = (size * 2) / (1024 * 1024 * ultra_total)
            
            print(f"    Round-trip: {ultra_total:.3f}s ({ultra_throughput:.1f} MB/s)")
            assert ultra_decrypted == test_data, "Ultra round-trip failed!"
        
        # Test Standard for comparison
        print("  Standard Cipher:")
        std_cipher = FaroCipher(key=get_key(args), profile=args.profile, rounds=args.rounds)
        
        import time
        start = time.perf_counter()
        std_encrypted = std_cipher.encrypt(test_data)
        std_encrypt_time = time.perf_counter() - start
        
        start = time.perf_counter()
        std_decrypted = std_cipher.decrypt(std_encrypted)
        std_decrypt_time = time.perf_counter() - start
        
        std_total = std_encrypt_time + std_decrypt_time
        std_throughput = (size * 2) / (1024 * 1024 * std_total)
        
        print(f"    Round-trip: {std_total:.3f}s ({std_throughput:.1f} MB/s)")
        assert std_decrypted == test_data, "Standard round-trip failed!"
        
        # Show speedup if both tested
        if not args.standard and std_total > 0:
            speedup = std_total / ultra_total
            print(f"    Ultra speedup: {speedup:.1f}x")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        prog='cliopatra',
        description="Cliopatra - Ultra-Optimized Faro Cipher CLI\nSecure encryption using shuffle-based operations with algorithmic optimizations!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encrypt text with ultra performance (default)
  python cliopatra.py encrypt-text --profile performance -t "Hello, World!"
  
  # Encrypt large file with ultra streaming
  python cliopatra.py encrypt-file -i document.pdf -o document.enc
  
  # Use standard implementation for compatibility testing
  python cliopatra.py --standard encrypt-text -t "Test message"
  
  # Benchmark performance
  python cliopatra.py benchmark -k "test-key"
  
  # Show ultra optimizations info
  python cliopatra.py info -k "test-key"
        """
    )
    
    # Global arguments
    parser.add_argument('--profile', '-p', choices=['performance', 'balanced', 'maximum'],
                       default='balanced', help='Security profile (default: balanced)')
    parser.add_argument('--key', '-k', help='Encryption key (will prompt if not provided)')
    parser.add_argument('--key-file', help='File containing encryption key')
    parser.add_argument('--rounds', '-r', type=int, help='Custom number of rounds (1-100, overrides profile)')
    parser.add_argument('--standard', action='store_true', help='Use standard implementation instead of ultra')
    parser.add_argument('--no-cache', action='store_true', help='Disable cache optimization (ultra only)')
    parser.add_argument('--force', action='store_true', help='Force operation despite warnings')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encrypt text
    encrypt_text_parser = subparsers.add_parser('encrypt-text', help='Encrypt text data')
    encrypt_text_parser.add_argument('--text', '-t', help='Text to encrypt (will prompt if not provided)')
    encrypt_text_parser.add_argument('--output', '-o', help='Output file (JSON format)')
    
    # Decrypt text
    decrypt_text_parser = subparsers.add_parser('decrypt-text', help='Decrypt text data')
    decrypt_text_parser.add_argument('--input', '-i', help='Input file (JSON format)')
    decrypt_text_parser.add_argument('--output', '-o', help='Output file')
    
    # Encrypt file
    encrypt_file_parser = subparsers.add_parser('encrypt-file', help='Encrypt a file')
    encrypt_file_parser.add_argument('--input', '-i', required=True, help='Input file to encrypt')
    encrypt_file_parser.add_argument('--output', '-o', required=True, help='Output encrypted file')
    
    # Decrypt file
    decrypt_file_parser = subparsers.add_parser('decrypt-file', help='Decrypt a file')
    decrypt_file_parser.add_argument('--input', '-i', required=True, help='Encrypted input file')
    decrypt_file_parser.add_argument('--output', '-o', required=True, help='Output decrypted file')
    
    # Info
    info_parser = subparsers.add_parser('info', help='Show cipher information')
    
    # Benchmark
    benchmark_parser = subparsers.add_parser('benchmark', help='Benchmark cipher performance')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'encrypt-text':
        encrypt_text(args)
    elif args.command == 'decrypt-text':
        decrypt_text(args)
    elif args.command == 'encrypt-file':
        encrypt_file(args)
    elif args.command == 'decrypt-file':
        decrypt_file(args)
    elif args.command == 'info':
        show_info(args)
    elif args.command == 'benchmark':
        benchmark_cipher(args)

if __name__ == '__main__':
    main() 