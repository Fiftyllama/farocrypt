#!/usr/bin/env python3
"""
Faro Cipher Release Test Suite
=============================

Simple test suite to verify core functionality for release.
Tests both the Python API and CLI tool.

License: WTFPL v2 - Do whatever you want with this code.
SPDX-License-Identifier: WTFPL
"""

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path
import hashlib

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        from faro_cipher import FaroCipher, UltraFaroCipher
        print("  Core imports successful")
        return True
    except ImportError as e:
        print(f"  Import failed: {e}")
        return False

def test_basic_encryption():
    """Test basic encryption/decryption with both implementations"""
    print("Testing basic encryption...")
    
    try:
        from faro_cipher import FaroCipher, UltraFaroCipher
        
        test_data = b"Hello, World! This is a test message."
        key = b"test-key-12345"
        
        # Test Standard Cipher
        std_cipher = FaroCipher(key=key, profile="performance")
        std_encrypted = std_cipher.encrypt(test_data)
        std_decrypted = std_cipher.decrypt(std_encrypted)
        
        if std_decrypted != test_data:
            print("  Standard cipher round-trip failed")
            return False
        print("  Standard cipher round-trip successful")
        
        # Test Ultra Cipher
        ultra_cipher = UltraFaroCipher(key=key, profile="performance")
        ultra_encrypted = ultra_cipher.encrypt(test_data)
        ultra_decrypted = ultra_cipher.decrypt(ultra_encrypted)
        
        if ultra_decrypted != test_data:
            print("  Ultra cipher round-trip failed")
            return False
        print("  Ultra cipher round-trip successful")
        
        return True
        
    except Exception as e:
        print(f"  Encryption test failed: {e}")
        return False

def test_different_profiles():
    """Test different security profiles"""
    print("Testing security profiles...")
    
    try:
        from faro_cipher import UltraFaroCipher
        
        test_data = b"Profile test data"
        key = b"profile-test-key"
        
        profiles = ["performance", "balanced", "maximum"]
        
        for profile in profiles:
            cipher = UltraFaroCipher(key=key, profile=profile)
            encrypted = cipher.encrypt(test_data)
            decrypted = cipher.decrypt(encrypted)
            
            if decrypted != test_data:
                print(f"  Profile '{profile}' failed")
                return False
            print(f"  Profile '{profile}' working")
        
        return True
        
    except Exception as e:
        print(f"  Profile test failed: {e}")
        return False

def test_performance():
    """Basic performance test"""
    print("Testing performance...")
    
    try:
        from faro_cipher import FaroCipher, UltraFaroCipher
        
        # Test with 10KB data
        test_data = os.urandom(10 * 1024)
        key = b"perf-test-key"
        
        # Test Ultra performance
        ultra_cipher = UltraFaroCipher(key=key, profile="performance")
        
        start_time = time.perf_counter()
        ultra_encrypted = ultra_cipher.encrypt(test_data)
        ultra_decrypted = ultra_cipher.decrypt(ultra_encrypted)
        ultra_time = time.perf_counter() - start_time
        
        if ultra_decrypted != test_data:
            print("  Ultra performance test failed - data mismatch")
            return False
        
        ultra_throughput = (len(test_data) * 2) / (1024 * 1024 * ultra_time)
        print(f"  Ultra throughput: {ultra_throughput:.1f} MB/s")
        
        # Test Standard performance
        std_cipher = FaroCipher(key=key, profile="performance") 
        
        start_time = time.perf_counter()
        std_encrypted = std_cipher.encrypt(test_data)
        std_decrypted = std_cipher.decrypt(std_encrypted)
        std_time = time.perf_counter() - start_time
        
        if std_decrypted != test_data:
            print("  Standard performance test failed - data mismatch")
            return False
            
        std_throughput = (len(test_data) * 2) / (1024 * 1024 * std_time)
        speedup = ultra_throughput / std_throughput if std_throughput > 0 else 0
        
        print(f"  Standard throughput: {std_throughput:.1f} MB/s")
        print(f"  Ultra speedup: {speedup:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"  Performance test failed: {e}")
        return False

def test_cli_basic():
    """Test basic CLI functionality"""
    print("Testing CLI...")
    
    try:
        # Test CLI help
        result = subprocess.run([sys.executable, "cliopatra.py", "--help"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print("  CLI help failed")
            return False
        print("  CLI help working")
        
        # Test CLI info
        result = subprocess.run([sys.executable, "cliopatra.py", "--key", "test", "info"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"  CLI info failed: {result.stderr}")
            return False
        print("  CLI info working")
        
        return True
        
    except Exception as e:
        print(f"  CLI test failed: {e}")
        return False

def test_cli_text_encryption():
    """Test CLI text encryption/decryption"""
    print("Testing CLI text encryption...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test.json")
            
            # Encrypt text
            result = subprocess.run([
                sys.executable, "cliopatra.py", 
                "--key", "cli-test-key",
                "encrypt-text", 
                "--text", "Hello from CLI test!",
                "--output", output_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"  CLI text encryption failed: {result.stderr}")
                return False
            
            if not os.path.exists(output_file):
                print("  CLI encryption output file not created")
                return False
            
            # Decrypt text
            result = subprocess.run([
                sys.executable, "cliopatra.py",
                "--key", "cli-test-key", 
                "decrypt-text",
                "--input", output_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"  CLI text decryption failed: {result.stderr}")
                return False
            
            if "Hello from CLI test!" not in result.stdout:
                print("  CLI decryption output incorrect")
                return False
            
            print("  CLI text encryption/decryption working")
            return True
            
    except Exception as e:
        print(f"  CLI text test failed: {e}")
        return False

def test_file_encryption():
    """Test comprehensive file encryption/decryption round trips"""
    print("Testing file encryption...")
    
    try:
        from faro_cipher import UltraFaroCipher, FaroCipher
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test multiple file sizes and types
            test_cases = [
                ("small.txt", "Small text file", b"Hello, World! This is a small test file.\n"),
                ("medium.bin", "Medium binary file", os.urandom(50 * 1024)),  # 50KB
                ("large.dat", "Large data file", os.urandom(1024 * 1024)),   # 1MB
            ]
            
            print("  Testing Ultra cipher file streaming...")
            
            for filename, description, content in test_cases:
                test_file = os.path.join(temp_dir, filename)
                encrypted_file = os.path.join(temp_dir, f"{filename}.enc")
                decrypted_file = os.path.join(temp_dir, f"{filename}.dec")
                
                # Write test file
                with open(test_file, 'wb') as f:
                    f.write(content)
                
                # Calculate original hash
                original_hash = hashlib.sha256(content).hexdigest()
                
                # Test Ultra cipher with file streaming
                ultra_cipher = UltraFaroCipher(key=b"ultra-file-test-key", profile="performance")
                
                # Encrypt using ultra streaming
                if hasattr(ultra_cipher, 'encrypt_file_ultra'):
                    metadata = ultra_cipher.encrypt_file_ultra(test_file, encrypted_file, progress=False)
                else:
                    metadata = ultra_cipher.encrypt_file(test_file, encrypted_file)
                
                if not os.path.exists(encrypted_file):
                    print(f"    Ultra encryption failed for {description} - no output file")
                    return False
                
                # Decrypt using ultra streaming
                if hasattr(ultra_cipher, 'decrypt_file_ultra'):
                    success = ultra_cipher.decrypt_file_ultra(encrypted_file, decrypted_file, metadata, progress=False)
                else:
                    success = ultra_cipher.decrypt_file(encrypted_file, decrypted_file, metadata)
                
                if not success or not os.path.exists(decrypted_file):
                    print(f"    Ultra decryption failed for {description}")
                    return False
                
                # Verify content with hash comparison
                with open(decrypted_file, 'rb') as f:
                    decrypted_content = f.read()
                
                decrypted_hash = hashlib.sha256(decrypted_content).hexdigest()
                
                if original_hash != decrypted_hash:
                    print(f"    Hash mismatch for {description}!")
                    print(f"      Original:  {original_hash}")
                    print(f"      Decrypted: {decrypted_hash}")
                    return False
                
                print(f"    ✓ {description} ({len(content)//1024 if len(content) >= 1024 else len(content)}{'KB' if len(content) >= 1024 else 'B'}) - Perfect round trip")
            
            # Test Standard cipher for compatibility
            print("  Testing Standard cipher file encryption...")
            test_file = os.path.join(temp_dir, "standard_test.txt")
            encrypted_file = os.path.join(temp_dir, "standard_test.enc")
            decrypted_file = os.path.join(temp_dir, "standard_test.dec")
            
            test_content = b"Standard cipher test content for compatibility verification."
            
            with open(test_file, 'wb') as f:
                f.write(test_content)
            
            original_hash = hashlib.sha256(test_content).hexdigest()
            
            std_cipher = FaroCipher(key=b"std-file-test-key", profile="performance")
            
            metadata = std_cipher.encrypt_file(test_file, encrypted_file)
            success = std_cipher.decrypt_file(encrypted_file, decrypted_file, metadata)
            
            if not success:
                print("    Standard cipher file encryption failed")
                return False
            
            with open(decrypted_file, 'rb') as f:
                decrypted_content = f.read()
            
            decrypted_hash = hashlib.sha256(decrypted_content).hexdigest()
            
            if original_hash != decrypted_hash:
                print("    Standard cipher hash mismatch!")
                return False
            
            print("    ✓ Standard cipher compatibility verified")
            
            print("  File encryption/decryption working")
            return True
            
    except Exception as e:
        print(f"  File encryption test failed: {e}")
        return False

def test_cli_file_round_trip():
    """Test CLI file encryption/decryption round trip"""
    print("Testing CLI file round trip...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file with binary content
            test_file = os.path.join(temp_dir, "cli_test.bin")
            encrypted_file = os.path.join(temp_dir, "cli_test.enc")
            decrypted_file = os.path.join(temp_dir, "cli_test.dec")
            
            # Mix of text and binary data
            test_content = b"CLI Test File\x00\x01\x02\x03\xFF\xFE\xFD" + os.urandom(1024)
            
            with open(test_file, 'wb') as f:
                f.write(test_content)
            
            original_hash = hashlib.sha256(test_content).hexdigest()
            
            # Encrypt via CLI
            result = subprocess.run([
                sys.executable, "cliopatra.py",
                "--key", "cli-round-trip-key",
                "encrypt-file",
                "-i", test_file,
                "-o", encrypted_file
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"    CLI file encryption failed: {result.stderr}")
                return False
            
            if not os.path.exists(encrypted_file):
                print("    CLI encryption did not create output file")
                return False
            
            if not os.path.exists(f"{encrypted_file}.meta"):
                print("    CLI encryption did not create metadata file")
                return False
            
            # Decrypt via CLI
            result = subprocess.run([
                sys.executable, "cliopatra.py",
                "--key", "cli-round-trip-key",
                "decrypt-file", 
                "-i", encrypted_file,
                "-o", decrypted_file
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"    CLI file decryption failed: {result.stderr}")
                return False
            
            if not os.path.exists(decrypted_file):
                print("    CLI decryption did not create output file")
                return False
            
            # Verify content
            with open(decrypted_file, 'rb') as f:
                decrypted_content = f.read()
            
            decrypted_hash = hashlib.sha256(decrypted_content).hexdigest()
            
            if original_hash != decrypted_hash:
                print("    CLI round trip hash mismatch!")
                print(f"      Original:  {original_hash}")
                print(f"      Decrypted: {decrypted_hash}")
                print(f"      Original size: {len(test_content)}")
                print(f"      Decrypted size: {len(decrypted_content)}")
                return False
            
            print(f"    ✓ CLI round trip verified ({len(test_content)} bytes)")
            print("  CLI file round trip working")
            return True
            
    except Exception as e:
        print(f"  CLI file round trip test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Faro Cipher Release Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_basic_encryption,
        test_different_profiles,
        test_performance,
        test_cli_basic,
        test_cli_text_encryption,
        test_file_encryption,
        test_cli_file_round_trip,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Blank line between tests
        except Exception as e:
            print(f"  Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Release ready.")
        return 0
    else:
        print("Some tests failed. Review before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 