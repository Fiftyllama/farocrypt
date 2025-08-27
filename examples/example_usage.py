#!/usr/bin/env python3
"""
Example usage of the Faro Cipher

This script demonstrates basic usage patterns for the improved Faro cipher.
"""

import tempfile
from pathlib import Path
from faro_cipher_improved import FaroCipher, EncryptionMetadata

def basic_example():
    """Basic encryption and decryption example"""
    print("=== Basic Faro Cipher Example ===\n")
    
    # Sample data
    message = "Hello, this is a secret message encrypted with the Faro cipher!"
    data = message.encode('utf-8')
    
    print(f"Original message: {message}")
    print(f"Data size: {len(data)} bytes\n")
    
    # Initialize cipher
    cipher = FaroCipher()
    
    # Define encryption pattern
    pattern = ["bin", "b64", "bin", "b64", "bin"]  # 5 rounds alternating domains
    strategy = "dualp2"  # Dual power-of-2 padding
    
    print(f"Encryption pattern: {pattern}")
    print(f"Padding strategy: {strategy}")
    print("Encrypting...\n")
    
    # Encrypt
    encrypted, metadata = cipher.encrypt(data, pattern, strategy)
    
    print(f"Encrypted (base64): {encrypted[:50]}..." if len(encrypted) > 50 else f"Encrypted: {encrypted}")
    print(f"Metadata rounds: {len(metadata.round_keys)}")
    print(f"Round keys: {metadata.round_keys}")
    print(f"Padded length: {metadata.b64_length} chars (base64)")
    print(f"Original length: {metadata.original_length} bytes\n")
    
    # Decrypt
    print("Decrypting...")
    decrypted = cipher.decrypt(encrypted, metadata)
    decrypted_message = decrypted.decode('utf-8')
    
    print(f"Decrypted message: {decrypted_message}")
    print(f"✅ Success: {'✓' if decrypted_message == message else '✗'}\n")

def file_example():
    """File encryption/decryption example"""
    print("=== File Encryption Example ===\n")
    
    # Create temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample file
        input_file = temp_path / "secret_document.txt"
        sample_content = """
This is a confidential document that contains important information.

It has multiple lines and various characters:
- Special symbols: !@#$%^&*()
- Numbers: 1234567890
- Unicode: 🔒🔑🎲
- Binary data would also work fine!

The Faro cipher can handle any binary data.
        """.strip()
        
        with open(input_file, "w", encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"Created input file: {input_file.name}")
        print(f"File size: {input_file.stat().st_size} bytes")
        
        # Read and encrypt
        with open(input_file, "rb") as f:
            file_data = f.read()
        
        cipher = FaroCipher()
        pattern = ["bin", "b64", "bin", "b64", "bin", "b64", "bin"]  # 7 rounds
        
        print(f"Encrypting with {len(pattern)} rounds...")
        encrypted, metadata = cipher.encrypt(file_data, pattern, "longcycle")
        
        # Save encrypted files
        enc_file = temp_path / "secret_document.txt.enc"
        meta_file = temp_path / "secret_document.txt.enc.meta.json"
        
        with open(enc_file, "w") as f:
            f.write(encrypted)
        
        import json
        from dataclasses import asdict
        with open(meta_file, "w") as f:
            json.dump(asdict(metadata), f, indent=2)
        
        print(f"Saved encrypted file: {enc_file.name} ({enc_file.stat().st_size} bytes)")
        print(f"Saved metadata: {meta_file.name} ({meta_file.stat().st_size} bytes)")
        
        # Decrypt and verify
        with open(enc_file, "r") as f:
            enc_data = f.read()
        
        with open(meta_file, "r") as f:
            meta_dict = json.load(f)
            loaded_metadata = EncryptionMetadata(**meta_dict)
        
        print("Decrypting...")
        decrypted = cipher.decrypt(enc_data, loaded_metadata)
        
        # Save decrypted file
        dec_file = temp_path / "decrypted_document.txt"
        with open(dec_file, "wb") as f:
            f.write(decrypted)
        
        print(f"Saved decrypted file: {dec_file.name}")
        
        # Verify
        success = decrypted == file_data
        print(f"✅ Decryption successful: {'✓' if success else '✗'}")
        
        if success:
            print("\n📄 First 200 chars of decrypted content:")
            print(decrypted.decode('utf-8')[:200] + "..." if len(decrypted) > 200 else decrypted.decode('utf-8'))

def performance_example():
    """Performance demonstration with different strategies"""
    print("=== Performance Comparison ===\n")
    
    import time
    
    # Test data sizes
    sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
    strategies = ["exact", "power2", "dualp2"]
    
    for size in sizes:
        print(f"Testing with {size} bytes ({size/1024:.1f}KB):")
        test_data = b"X" * size
        
        for strategy in strategies:
            cipher = FaroCipher()
            pattern = ["bin", "b64", "bin"]  # Simple 3-round pattern
            
            # Time encryption
            start_time = time.time()
            encrypted, metadata = cipher.encrypt(test_data, pattern, strategy)
            encrypt_time = time.time() - start_time
            
            # Time decryption
            start_time = time.time()
            decrypted = cipher.decrypt(encrypted, metadata)
            decrypt_time = time.time() - start_time
            
            success = decrypted == test_data
            expansion = len(encrypted) / len(test_data)
            
            print(f"  {strategy:8}: encrypt={encrypt_time:.3f}s, decrypt={decrypt_time:.3f}s, "
                  f"expansion={expansion:.2f}x, success={'✓' if success else '✗'}")
        
        print()

def main():
    """Run all examples"""
    print("🎲 Faro Cipher Examples\n")
    
    try:
        basic_example()
        file_example()
        performance_example()
        
        print("🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 