#!/usr/bin/env python3
"""
Comprehensive Test: Ultra-Optimized Faro Cipher Full Functionality
Tests encryption, decryption, and file integrity verification
"""

import os
import time
import hashlib
import secrets
from pathlib import Path
import traceback

def create_test_file(filename: str, size_kb: int = 10, content_type: str = "text") -> str:
    """Create a test file with various content types"""
    size_bytes = size_kb * 1024
    
    with open(filename, 'wb') as f:
        if content_type == "text":
            # Text content
            pattern = b"This is a comprehensive test of the ultra-optimized Faro cipher. " \
                     b"We need to verify that encryption and decryption work perfectly. " \
                     b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " \
                     b"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        elif content_type == "binary":
            # Binary content
            pattern = bytes(range(256)) * 4  # All possible byte values
        elif content_type == "random":
            # Random content
            pattern = secrets.token_bytes(1024)
        else:
            pattern = b"default test content " * 50
        
        remaining = size_bytes
        while remaining > 0:
            write_size = min(len(pattern), remaining)
            f.write(pattern[:write_size])
            remaining -= write_size
    
    return filename

def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA256 hash of a file"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(32768), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def test_encrypt_decrypt_cycle(test_name: str, file_size_kb: int, content_type: str = "text") -> dict:
    """Test a complete encrypt/decrypt cycle"""
    
    print(f"\n🧪 Testing: {test_name}")
    print("=" * 60)
    
    try:
        from faro_cipher_ultra_optimized import UltraOptimizedFaroCipher
        
        # Create test file
        original_file = f"test_{test_name.lower().replace(' ', '_')}.dat"
        create_test_file(original_file, file_size_kb, content_type)
        
        # Calculate original hash
        original_hash = calculate_file_hash(original_file)
        original_size = Path(original_file).stat().st_size
        
        print(f"📄 Original file: {original_size:,} bytes")
        print(f"🔍 Original SHA256: {original_hash[:16]}...")
        
        # Initialize cipher
        cipher = UltraOptimizedFaroCipher(chunk_size=4096)
        
        # === ENCRYPTION ===
        encrypted_file = original_file + ".ultra.enc"
        
        print(f"\n🔐 Encrypting...")
        encrypt_start = time.time()
        metadata = cipher.encrypt_file(original_file, encrypted_file, num_rounds=4, progress=False)
        encrypt_time = time.time() - encrypt_start
        
        encrypted_size = Path(encrypted_file).stat().st_size
        encrypt_throughput = original_size / (1024 * 1024) / encrypt_time if encrypt_time > 0 else 0
        
        print(f"   ✅ Encrypted in {encrypt_time:.3f}s ({encrypt_throughput:.2f} MB/s)")
        print(f"   📦 Encrypted size: {encrypted_size:,} bytes ({encrypted_size/original_size:.2f}x)")
        
        # === DECRYPTION ===
        decrypted_file = original_file + ".decrypted"
        
        print(f"\n🔓 Decrypting...")
        decrypt_start = time.time()
        success = cipher.decrypt_file(encrypted_file, decrypted_file, metadata, progress=False)
        decrypt_time = time.time() - decrypt_start
        
        if not success:
            raise Exception("Decryption failed")
        
        decrypted_size = Path(decrypted_file).stat().st_size
        decrypt_throughput = decrypted_size / (1024 * 1024) / decrypt_time if decrypt_time > 0 else 0
        
        print(f"   ✅ Decrypted in {decrypt_time:.3f}s ({decrypt_throughput:.2f} MB/s)")
        print(f"   📄 Decrypted size: {decrypted_size:,} bytes")
        
        # === VERIFICATION ===
        print(f"\n🔍 Verifying integrity...")
        
        # Check file sizes
        if decrypted_size != original_size:
            raise Exception(f"Size mismatch: {decrypted_size} != {original_size}")
        
        # Check file content hash
        decrypted_hash = calculate_file_hash(decrypted_file)
        
        if decrypted_hash != original_hash:
            raise Exception(f"Hash mismatch: {decrypted_hash} != {original_hash}")
        
        # Byte-by-byte comparison
        with open(original_file, 'rb') as f1, open(decrypted_file, 'rb') as f2:
            while True:
                chunk1 = f1.read(4096)
                chunk2 = f2.read(4096)
                
                if chunk1 != chunk2:
                    raise Exception("Byte-by-byte comparison failed")
                
                if not chunk1:  # End of file
                    break
        
        print(f"   ✅ Size verification: PASSED")
        print(f"   ✅ Hash verification: PASSED")
        print(f"   ✅ Byte-by-byte verification: PASSED")
        
        # Cleanup
        os.remove(original_file)
        os.remove(encrypted_file)
        os.remove(decrypted_file)
        
        result = {
            'test_name': test_name,
            'success': True,
            'original_size': original_size,
            'encrypted_size': encrypted_size,
            'encrypt_time': encrypt_time,
            'decrypt_time': decrypt_time,
            'encrypt_throughput': encrypt_throughput,
            'decrypt_throughput': decrypt_throughput,
            'compression_ratio': encrypted_size / original_size,
            'integrity_verified': True
        }
        
        print(f"\n✅ {test_name}: PASSED")
        
        return result
        
    except Exception as e:
        print(f"\n❌ {test_name}: FAILED")
        print(f"   Error: {e}")
        traceback.print_exc()
        
        # Cleanup on failure
        for file in [original_file, encrypted_file, decrypted_file]:
            if os.path.exists(file):
                os.remove(file)
        
        return {
            'test_name': test_name,
            'success': False,
            'error': str(e)
        }

def run_comprehensive_functionality_test():
    """Run comprehensive tests of the ultra-optimized cipher"""
    
    print("🚀 COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 80)
    print("Ultra-Optimized Faro Cipher: Encryption + Decryption + Verification")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        ("Small Text File", 1, "text"),
        ("Medium Text File", 10, "text"),
        ("Large Text File", 100, "text"),
        ("Small Binary File", 5, "binary"),
        ("Medium Binary File", 50, "binary"),
        ("Random Data File", 25, "random"),
        ("Large Random File", 200, "random"),
    ]
    
    results = []
    successful_tests = 0
    
    for test_name, size_kb, content_type in test_cases:
        result = test_encrypt_decrypt_cycle(test_name, size_kb, content_type)
        results.append(result)
        
        if result['success']:
            successful_tests += 1
    
    # Summary
    print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    print(f"{'Test Name':<25} {'Status':<10} {'Size':<12} {'Enc Time':<10} {'Dec Time':<10} {'Integrity'}")
    print("-" * 80)
    
    total_encrypt_time = 0
    total_decrypt_time = 0
    total_size = 0
    
    for result in results:
        if result['success']:
            status = "✅ PASS"
            size_str = f"{result['original_size']:,}B"
            enc_time = f"{result['encrypt_time']:.3f}s"
            dec_time = f"{result['decrypt_time']:.3f}s"
            integrity = "✅ OK" if result['integrity_verified'] else "❌ FAIL"
            
            total_encrypt_time += result['encrypt_time']
            total_decrypt_time += result['decrypt_time']
            total_size += result['original_size']
        else:
            status = "❌ FAIL"
            size_str = "N/A"
            enc_time = "N/A"
            dec_time = "N/A"
            integrity = "❌ FAIL"
        
        print(f"{result['test_name']:<25} {status:<10} {size_str:<12} {enc_time:<10} {dec_time:<10} {integrity}")
    
    # Overall statistics
    print(f"\n📈 OVERALL STATISTICS")
    print("=" * 40)
    print(f"Tests passed: {successful_tests}/{len(test_cases)} ({successful_tests/len(test_cases)*100:.1f}%)")
    
    if successful_tests > 0:
        avg_encrypt_throughput = (total_size / (1024 * 1024)) / total_encrypt_time if total_encrypt_time > 0 else 0
        avg_decrypt_throughput = (total_size / (1024 * 1024)) / total_decrypt_time if total_decrypt_time > 0 else 0
        
        print(f"Total data processed: {total_size:,} bytes")
        print(f"Total encryption time: {total_encrypt_time:.2f}s")
        print(f"Total decryption time: {total_decrypt_time:.2f}s")
        print(f"Average encryption throughput: {avg_encrypt_throughput:.2f} MB/s")
        print(f"Average decryption throughput: {avg_decrypt_throughput:.2f} MB/s")
        
        # Check encryption vs decryption speed
        speed_ratio = avg_decrypt_throughput / avg_encrypt_throughput if avg_encrypt_throughput > 0 else 0
        print(f"Decryption speed vs encryption: {speed_ratio:.1f}x")
        
        # File size analysis
        successful_results = [r for r in results if r['success']]
        avg_compression = sum(r['compression_ratio'] for r in successful_results) / len(successful_results)
        print(f"Average file size ratio: {avg_compression:.2f}x")
    
    # Final verdict
    print(f"\n🎉 FINAL VERDICT")
    print("=" * 30)
    
    if successful_tests == len(test_cases):
        print("✅ ALL TESTS PASSED! The ultra-optimized cipher is FULLY FUNCTIONAL!")
        print("✅ Encryption and decryption work perfectly")
        print("✅ File integrity is maintained across all test cases")
        print("✅ Performance is excellent on all file types and sizes")
        print("\n🚀 The cipher is ready for production use!")
    elif successful_tests > len(test_cases) * 0.8:
        print("⚠️  MOSTLY FUNCTIONAL - Most tests passed")
        print(f"⚠️  {len(test_cases) - successful_tests} test(s) failed")
        print("⚠️  Review failed tests before production use")
    else:
        print("❌ CRITICAL ISSUES - Many tests failed")
        print("❌ The cipher needs significant fixes before use")
    
    return successful_tests == len(test_cases)

if __name__ == "__main__":
    print("🧪 Testing Ultra-Optimized Faro Cipher Full Functionality")
    print("Comprehensive Encrypt/Decrypt/Verify Test Suite")
    print("=" * 80)
    
    try:
        success = run_comprehensive_functionality_test()
        
        if success:
            print("\n🏆 All functionality tests completed successfully!")
            exit(0)
        else:
            print("\n💥 Some functionality tests failed!")
            exit(1)
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        traceback.print_exc()
        exit(1) 