#!/usr/bin/env python3
"""
File Encryption Example
=======================

Example showing how to encrypt and decrypt files with Faro Cipher.
"""

import os
import json
from pathlib import Path
from faro_cipher import FaroCipher

def create_sample_file(filename: str, content: str):
    """Create a sample file for testing"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📝 Created sample file: {filename}")

def file_encryption_example():
    """Demonstrate file encryption and decryption"""
    print("📁 File Encryption Example")
    print("="*30)
    
    # Create sample content
    sample_content = """
This is a sample text file for demonstrating Faro Cipher file encryption.

The file contains multiple lines of text, including:
- Special characters: !@#$%^&*()
- Numbers: 1234567890
- Unicode: 你好世界 🌍 🔐
- Various punctuation and symbols

The Faro Cipher will encrypt this entire file while preserving
all the content exactly as it appears here.
    """.strip()
    
    # File names
    original_file = "sample.txt"
    encrypted_file = "sample.txt.encrypted"
    decrypted_file = "sample_decrypted.txt"
    metadata_file = "sample.metadata.json"
    
    try:
        # Create sample file
        create_sample_file(original_file, sample_content)
        
        # Create cipher
        cipher = FaroCipher(key=b"file-encryption-key", profile="balanced")
        
        print(f"\n🔐 Encrypting file: {original_file}")
        # Encrypt file
        metadata = cipher.encrypt_file(original_file, encrypted_file)
        
        # Save metadata
        metadata_dict = {
            'version': metadata.version,
            'profile': metadata.profile,
            'rounds': metadata.rounds,
            'chunk_size': metadata.chunk_size,
            'key_fingerprint': metadata.key_fingerprint,
            'chunk_sizes': metadata.chunk_sizes,
            'round_structure': metadata.round_structure
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
        
        print(f"✅ File encrypted successfully!")
        print(f"📄 Original size: {os.path.getsize(original_file)} bytes")
        print(f"🔒 Encrypted size: {os.path.getsize(encrypted_file)} bytes")
        print(f"📋 Metadata saved to: {metadata_file}")
        
        print(f"\n🔓 Decrypting file: {encrypted_file}")
        # Decrypt file
        success = cipher.decrypt_file(encrypted_file, decrypted_file, metadata)
        
        if success:
            print(f"✅ File decrypted successfully!")
            print(f"📄 Decrypted size: {os.path.getsize(decrypted_file)} bytes")
            
            # Verify content
            with open(original_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(decrypted_file, 'r', encoding='utf-8') as f:
                decrypted_content = f.read()
            
            if original_content == decrypted_content:
                print("✅ Content verification: PERFECT MATCH")
            else:
                print("❌ Content verification: MISMATCH")
                print(f"Original length: {len(original_content)}")
                print(f"Decrypted length: {len(decrypted_content)}")
        else:
            print("❌ Decryption failed!")
            
    finally:
        # Cleanup
        for file in [original_file, encrypted_file, decrypted_file, metadata_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️ Cleaned up: {file}")

def large_file_example():
    """Demonstrate encryption of a larger file"""
    print("\n📦 Large File Example")
    print("="*25)
    
    # Create a larger sample file
    large_content = "This is a line of text for the large file test.\n" * 1000
    large_file = "large_sample.txt"
    encrypted_large = "large_sample.encrypted"
    decrypted_large = "large_sample_decrypted.txt"
    
    try:
        create_sample_file(large_file, large_content)
        print(f"📄 Large file size: {os.path.getsize(large_file)} bytes")
        
        # Use maximum security for large file
        cipher = FaroCipher(key=b"large-file-key", profile="maximum", chunk_size=4096)
        
        print("🔐 Encrypting large file...")
        metadata = cipher.encrypt_file(large_file, encrypted_large)
        print(f"✅ Encrypted! Size: {os.path.getsize(encrypted_large)} bytes")
        
        print("🔓 Decrypting large file...")
        success = cipher.decrypt_file(encrypted_large, decrypted_large, metadata)
        
        if success:
            # Quick verification
            original_size = os.path.getsize(large_file)
            decrypted_size = os.path.getsize(decrypted_large)
            print(f"✅ Decryption complete!")
            print(f"📊 Size verification: {original_size} → {decrypted_size} ({'✅ MATCH' if original_size == decrypted_size else '❌ MISMATCH'})")
        
    finally:
        # Cleanup
        for file in [large_file, encrypted_large, decrypted_large]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️ Cleaned up: {file}")

def binary_file_example():
    """Demonstrate binary file encryption"""
    print("\n🔢 Binary File Example")
    print("="*25)
    
    binary_file = "binary_sample.bin"
    encrypted_binary = "binary_sample.encrypted"
    decrypted_binary = "binary_sample_decrypted.bin"
    
    try:
        # Create binary data
        binary_data = bytes(range(256)) * 10  # Repeating 0-255 pattern
        
        with open(binary_file, 'wb') as f:
            f.write(binary_data)
        
        print(f"📄 Binary file created: {len(binary_data)} bytes")
        print(f"🔍 First 16 bytes: {binary_data[:16].hex()}")
        
        # Encrypt
        cipher = FaroCipher(key=b"binary-key", profile="performance")
        metadata = cipher.encrypt_file(binary_file, encrypted_binary)
        print(f"🔐 Encrypted binary file")
        
        # Decrypt
        success = cipher.decrypt_file(encrypted_binary, decrypted_binary, metadata)
        
        if success:
            # Verify binary content
            with open(decrypted_binary, 'rb') as f:
                decrypted_data = f.read()
            
            if binary_data == decrypted_data:
                print("✅ Binary verification: PERFECT MATCH")
                print(f"🔍 First 16 bytes: {decrypted_data[:16].hex()}")
            else:
                print("❌ Binary verification: MISMATCH")
        
    finally:
        # Cleanup
        for file in [binary_file, encrypted_binary, decrypted_binary]:
            if os.path.exists(file):
                os.remove(file)

def main():
    """Run all file encryption examples"""
    print("🚀 Faro Cipher - File Encryption Examples")
    print("="*45)
    
    file_encryption_example()
    large_file_example()
    binary_file_example()
    
    print("\n🎉 All file encryption examples completed!")

if __name__ == "__main__":
    main() 