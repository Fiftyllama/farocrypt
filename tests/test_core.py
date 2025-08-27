#!/usr/bin/env python3
"""
Core Faro Cipher Tests
=====================

Test the main FaroCipher class functionality.
"""

import unittest
import tempfile
import os
from faro_cipher import FaroCipher

class TestFaroCipher(unittest.TestCase):
    """Test the main FaroCipher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_key = b"test-key-12345"
        self.test_data = b"Hello, World! This is a test message for Faro Cipher."
        
    def test_basic_encryption_decryption(self):
        """Test basic encrypt/decrypt cycle"""
        cipher = FaroCipher(key=self.test_key, profile="performance")
        
        # Encrypt
        encrypted_result = cipher.encrypt(self.test_data)
        self.assertIn('encrypted_data', encrypted_result)
        self.assertIn('metadata', encrypted_result)
        
        # Decrypt
        decrypted_data = cipher.decrypt(encrypted_result)
        self.assertEqual(self.test_data, decrypted_data)
    
    def test_string_encryption(self):
        """Test string encryption/decryption"""
        cipher = FaroCipher(key=self.test_key, profile="balanced")
        
        test_string = "Hello, Faro Cipher! 🔐"
        encrypted_result = cipher.encrypt(test_string)
        decrypted_data = cipher.decrypt(encrypted_result)
        
        self.assertEqual(test_string.encode('utf-8'), decrypted_data)
    
    def test_different_profiles(self):
        """Test all security profiles work correctly"""
        test_data = b"Profile test data"
        
        for profile in ["performance", "balanced", "maximum"]:
            with self.subTest(profile=profile):
                cipher = FaroCipher(key=self.test_key, profile=profile)
                
                encrypted_result = cipher.encrypt(test_data)
                decrypted_data = cipher.decrypt(encrypted_result)
                
                self.assertEqual(test_data, decrypted_data)
    
    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different encrypted results"""
        test_data = b"Key sensitivity test"
        
        cipher1 = FaroCipher(key=b"key1", profile="performance")
        cipher2 = FaroCipher(key=b"key2", profile="performance")
        
        result1 = cipher1.encrypt(test_data)
        result2 = cipher2.encrypt(test_data)
        
        # Different keys should produce different encrypted data
        self.assertNotEqual(result1['encrypted_data'], result2['encrypted_data'])
        
        # But each should decrypt correctly with their own key
        self.assertEqual(test_data, cipher1.decrypt(result1))
        self.assertEqual(test_data, cipher2.decrypt(result2))
    
    def test_wrong_key_fails(self):
        """Test that wrong key fails to decrypt"""
        cipher1 = FaroCipher(key=b"correct-key", profile="performance")
        cipher2 = FaroCipher(key=b"wrong-key", profile="performance")
        
        encrypted_result = cipher1.encrypt(self.test_data)
        
        # Should raise ValueError for wrong key
        with self.assertRaises(ValueError):
            cipher2.decrypt(encrypted_result)
    
    def test_empty_data(self):
        """Test encryption of empty data"""
        cipher = FaroCipher(key=self.test_key, profile="performance")
        
        empty_data = b""
        encrypted_result = cipher.encrypt(empty_data)
        decrypted_data = cipher.decrypt(encrypted_result)
        
        self.assertEqual(empty_data, decrypted_data)
    
    def test_large_data(self):
        """Test encryption of larger data"""
        cipher = FaroCipher(key=self.test_key, profile="balanced")
        
        # Create 10KB of test data
        large_data = b"A" * 10240
        encrypted_result = cipher.encrypt(large_data)
        decrypted_data = cipher.decrypt(encrypted_result)
        
        self.assertEqual(large_data, decrypted_data)
    
    def test_binary_data(self):
        """Test encryption of binary data"""
        cipher = FaroCipher(key=self.test_key, profile="balanced")
        
        # Test with all possible byte values
        binary_data = bytes(range(256))
        encrypted_result = cipher.encrypt(binary_data)
        decrypted_data = cipher.decrypt(encrypted_result)
        
        self.assertEqual(binary_data, decrypted_data)
    
    def test_get_info(self):
        """Test cipher info method"""
        cipher = FaroCipher(key=self.test_key, profile="balanced")
        info = cipher.get_info()
        
        self.assertIn('profile', info)
        self.assertIn('description', info)
        self.assertIn('rounds', info)
        self.assertIn('chunk_size', info)
        self.assertIn('key_fingerprint', info)
        
        self.assertEqual(info['profile'], 'balanced')
        self.assertEqual(info['rounds'], 6)  # Balanced profile has 6 rounds

class TestFileEncryption(unittest.TestCase):
    """Test file encryption functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_key = b"file-test-key"
        self.cipher = FaroCipher(key=self.test_key, profile="performance")
        
    def test_file_encryption_decryption(self):
        """Test file encryption and decryption"""
        test_content = "This is test file content.\nWith multiple lines!\n"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            input_file = os.path.join(temp_dir, "input.txt")
            encrypted_file = os.path.join(temp_dir, "encrypted.bin")
            output_file = os.path.join(temp_dir, "output.txt")
            
            # Write test content
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Encrypt file
            metadata = self.cipher.encrypt_file(input_file, encrypted_file)
            self.assertTrue(os.path.exists(encrypted_file))
            
            # Decrypt file
            success = self.cipher.decrypt_file(encrypted_file, output_file, metadata)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify content
            with open(output_file, 'r', encoding='utf-8') as f:
                decrypted_content = f.read()
            
            self.assertEqual(test_content, decrypted_content)
    
    def test_binary_file_encryption(self):
        """Test binary file encryption"""
        binary_content = bytes(range(256)) * 4  # 1KB of binary data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "binary.bin")
            encrypted_file = os.path.join(temp_dir, "binary.encrypted")
            output_file = os.path.join(temp_dir, "binary_out.bin")
            
            # Write binary content
            with open(input_file, 'wb') as f:
                f.write(binary_content)
            
            # Encrypt and decrypt
            metadata = self.cipher.encrypt_file(input_file, encrypted_file)
            success = self.cipher.decrypt_file(encrypted_file, output_file, metadata)
            self.assertTrue(success)
            
            # Verify binary content
            with open(output_file, 'rb') as f:
                decrypted_content = f.read()
            
            self.assertEqual(binary_content, decrypted_content)

if __name__ == '__main__':
    unittest.main() 