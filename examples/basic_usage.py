#!/usr/bin/env python3
"""
Basic Faro Cipher Usage Example
==============================

Simple examples showing how to use the Faro Cipher package.
"""

from faro_cipher import FaroCipher

def basic_string_encryption():
    """Basic string encryption example"""
    print("🔐 Basic String Encryption Example")
    print("="*40)
    
    # Create cipher
    cipher = FaroCipher(key=b"my-secret-key", profile="balanced")
    
    # Encrypt a message
    message = "Hello, Faro Cipher! This is a secret message."
    print(f"Original message: {message}")
    
    # Encrypt
    encrypted_result = cipher.encrypt(message)
    encrypted_data = encrypted_result['encrypted_data']
    print(f"Encrypted data: {encrypted_data.hex()[:60]}...")
    print(f"Encrypted size: {len(encrypted_data)} bytes")
    
    # Decrypt
    decrypted_data = cipher.decrypt(encrypted_result)
    decrypted_message = decrypted_data.decode('utf-8')
    print(f"Decrypted message: {decrypted_message}")
    
    # Verify
    success = message == decrypted_message
    print(f"✅ Success: {success}")
    print()

def different_security_profiles():
    """Demonstrate different security profiles"""
    print("🛡️ Security Profiles Comparison")
    print("="*40)
    
    message = "This is a test message for comparing security profiles."
    
    for profile in ["performance", "balanced", "maximum"]:
        print(f"\n📋 Testing {profile.upper()} profile:")
        
        cipher = FaroCipher(key=b"test-key-123", profile=profile)
        
        # Show cipher info
        info = cipher.get_info()
        print(f"  Rounds: {info['rounds']}")
        print(f"  Description: {info['description']}")
        
        # Test encryption
        encrypted_result = cipher.encrypt(message)
        decrypted_data = cipher.decrypt(encrypted_result)
        
        success = message.encode() == decrypted_data
        print(f"  Test result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"  Encrypted size: {len(encrypted_result['encrypted_data'])} bytes")

def byte_data_encryption():
    """Example with binary data"""
    print("📁 Binary Data Encryption Example")
    print("="*40)
    
    # Create some binary data
    binary_data = bytes(range(256))  # 0-255
    print(f"Original data: {len(binary_data)} bytes")
    print(f"First 20 bytes: {binary_data[:20].hex()}")
    
    # Encrypt
    cipher = FaroCipher(key=b"binary-key", profile="balanced")
    encrypted_result = cipher.encrypt(binary_data)
    
    print(f"Encrypted size: {len(encrypted_result['encrypted_data'])} bytes")
    
    # Decrypt
    decrypted_data = cipher.decrypt(encrypted_result)
    print(f"Decrypted size: {len(decrypted_data)} bytes")
    print(f"First 20 bytes: {decrypted_data[:20].hex()}")
    
    # Verify
    success = binary_data == decrypted_data
    print(f"✅ Perfect match: {success}")
    print()

def main():
    """Run all examples"""
    print("🚀 Faro Cipher - Basic Usage Examples")
    print("="*50)
    print()
    
    basic_string_encryption()
    different_security_profiles()
    byte_data_encryption()
    
    print("🎉 All examples completed!")

if __name__ == "__main__":
    main() 