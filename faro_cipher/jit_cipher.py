"""
Faro Cipher JIT Optimized Implementation
=======================================

Ultra-high performance version using JIT compilation for all critical operations.
"""

import numpy as np
import time
from typing import Dict, Any, Union, Optional

from .core import FaroCipher, EncryptionMetadata
from .utils import verify_key_compatibility
from .jit_optimized import (
    process_single_chunk_jit, 
    TRANSFORM_TYPE_MAP, 
    SHUFFLE_TYPE_MAP,
    HAS_NUMBA
)

class JITFaroCipher(FaroCipher):
    """
    JIT-optimized Faro Cipher using Numba-compiled functions for maximum performance
    """
    
    def __init__(self, key: bytes, profile: str = "balanced", chunk_size: int = 8192, 
                 rounds: Optional[int] = None, warmup: bool = True):
        """
        Initialize JIT-optimized cipher
        
        Args:
            key: Encryption key
            profile: Security profile
            chunk_size: Base chunk size
            rounds: Number of rounds
            warmup: Whether to warm up JIT compilation with dummy data
        """
        super().__init__(key, profile, chunk_size, rounds)
        
        if not HAS_NUMBA:
            print("⚠️  Numba not available - JIT optimizations disabled")
        else:
            print(f"🚀 JIT Mode: Numba compilation enabled")
            
            if warmup:
                self._warmup_jit()
    
    def _warmup_jit(self):
        """Warm up JIT compilation with dummy data to avoid first-call overhead"""
        print("  🔥 Warming up JIT compilation...")
        start_time = time.perf_counter()
        
        # Small dummy data to trigger compilation
        dummy_bytes = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.uint8)
        
        # Compile all the JIT functions
        try:
            process_single_chunk_jit(
                dummy_bytes,
                shuffle_type=1,     # in
                shuffle_steps=1, 
                shuffle_variant=0,
                transform_type=0,   # enhanced_xor
                transform_key=12345,
                encrypt=True
            )
            
            process_single_chunk_jit(
                dummy_bytes,
                shuffle_type=1,     # in
                shuffle_steps=1, 
                shuffle_variant=0,
                transform_type=0,   # enhanced_xor
                transform_key=12345,
                encrypt=False
            )
            
            warmup_time = time.perf_counter() - start_time
            print(f"  ✅ JIT warmup completed in {warmup_time:.3f}s")
            
        except Exception as e:
            print(f"  ⚠️  JIT warmup failed: {e}")
    
    def _process_single_chunk_jit(self, chunk: bytes, round_info: Dict[str, Any], encrypt: bool) -> bytes:
        """Process a single chunk using JIT-optimized functions"""
        if len(chunk) == 0:
            return chunk
        
        if not HAS_NUMBA:
            # Fallback to original implementation
            return super()._process_single_chunk(chunk, round_info, encrypt)
        
        # Convert to numpy array for JIT function
        chunk_bytes = np.frombuffer(chunk, dtype=np.uint8)
        
        # Map string types to integers for JIT functions
        shuffle_type_int = SHUFFLE_TYPE_MAP.get(round_info['shuffle_type'], 0)
        transform_type_int = TRANSFORM_TYPE_MAP.get(round_info['transform_type'], 0)
        
        # Call JIT-optimized function
        result_bytes = process_single_chunk_jit(
            chunk_bytes,
            shuffle_type=shuffle_type_int,
            shuffle_steps=round_info['shuffle_steps'],
            shuffle_variant=round_info['shuffle_variant'],
            transform_type=transform_type_int,
            transform_key=round_info['transform_key'],
            encrypt=encrypt
        )
        
        return result_bytes.tobytes()
    
    def _apply_round_to_data_jit(self, data: bytes, round_info: Dict[str, Any], encrypt: bool, round_num: int) -> bytes:
        """Apply a round using JIT-optimized chunk processing"""
        chunk_size = round_info['round_chunk_size']
        
        # Split data into chunks
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        
        # Process each chunk with JIT optimization
        processed_chunks = []
        for chunk in chunks:
            processed_chunk = self._process_single_chunk_jit(chunk, round_info, encrypt)
            processed_chunks.append(processed_chunk)
        
        # Recombine chunks
        return b''.join(processed_chunks)
    
    def _process_data_variable_chunks_jit(self, data: bytes, encrypt: bool = True) -> bytes:
        """JIT-optimized data processing with variable chunks"""
        
        # Find the maximum chunk size across all rounds
        max_chunk_size = max(round_info['round_chunk_size'] for round_info in self.round_structure)
        
        # Pad data to be divisible by max chunk size at the start
        current_data = data
        
        if encrypt:
            # Pad to multiple of max chunk size
            padding_needed = (max_chunk_size - (len(data) % max_chunk_size)) % max_chunk_size
            if padding_needed > 0:
                # Use deterministic padding based on data content
                padding_byte = (sum(data) % 256) if data else 0
                current_data = data + bytes([padding_byte] * padding_needed)
        
        # Apply rounds with JIT optimization
        if encrypt:
            # Forward processing
            for round_num, round_info in enumerate(self.round_structure):
                current_data = self._apply_round_to_data_jit(
                    current_data, round_info, encrypt=True, round_num=round_num
                )
        else:
            # Reverse processing
            for round_num, round_info in enumerate(reversed(self.round_structure)):
                current_data = self._apply_round_to_data_jit(
                    current_data, round_info, encrypt=False, 
                    round_num=len(self.round_structure)-1-round_num
                )
        
        return current_data
    
    def encrypt(self, data: Union[bytes, str]) -> Dict[str, Any]:
        """
        JIT-optimized encryption
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        start_time = time.perf_counter()
        encrypted_data = self._process_data_variable_chunks_jit(data, encrypt=True)
        encrypt_time = time.perf_counter() - start_time
        
        metadata = EncryptionMetadata(
            version='faro_cipher_jit_v1.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=self.chunk_size,
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            original_size=len(data)
        )
        
        throughput = len(data) / (1024 * 1024 * encrypt_time) if encrypt_time > 0 else 0
        print(f"🚀 JIT encryption: {throughput:.1f} MB/s")
        
        return {
            'encrypted_data': encrypted_data,
            'metadata': metadata
        }
    
    def decrypt(self, encrypted_result: Dict[str, Any]) -> bytes:
        """
        JIT-optimized decryption
        """
        encrypted_data = encrypted_result['encrypted_data']
        metadata = encrypted_result['metadata']
        
        # Verify key compatibility
        if not verify_key_compatibility(self.key, metadata.key_fingerprint):
            raise ValueError("Key fingerprint mismatch - wrong key or corrupted metadata")
        
        start_time = time.perf_counter()
        decrypted_data = self._process_data_variable_chunks_jit(encrypted_data, encrypt=False)
        decrypt_time = time.perf_counter() - start_time
        
        # Trim to original size if specified
        if metadata.original_size is not None and len(decrypted_data) > metadata.original_size:
            decrypted_data = decrypted_data[:metadata.original_size]
        
        throughput = len(decrypted_data) / (1024 * 1024 * decrypt_time) if decrypt_time > 0 else 0
        print(f"🚀 JIT decryption: {throughput:.1f} MB/s")
        
        return decrypted_data
    
    def encrypt_file_jit(self, input_file: str, output_file: str, 
                        progress: bool = True) -> EncryptionMetadata:
        """
        JIT-optimized file encryption
        """
        import os
        from pathlib import Path
        
        file_size = Path(input_file).stat().st_size
        max_chunk_size = max(round_info['round_chunk_size'] for round_info in self.round_structure)
        
        # Use larger read chunks for file I/O efficiency
        read_chunk_size = max(max_chunk_size * 8, 1024 * 1024)  # At least 1MB reads
        
        if progress:
            print(f"🚀 JIT file encryption: {file_size//1024//1024}MB")
        
        chunk_sizes = []
        start_time = time.perf_counter()
        
        with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
            bytes_processed = 0
            
            while True:
                # Read larger chunks for better I/O performance
                data_chunk = infile.read(read_chunk_size)
                if not data_chunk:
                    break
                
                original_size = len(data_chunk)
                encrypted_chunk = self._process_data_variable_chunks_jit(data_chunk, encrypt=True)
                
                # Store chunk metadata and data
                chunk_sizes.append(original_size)
                outfile.write(len(encrypted_chunk).to_bytes(4, 'big'))
                outfile.write(encrypted_chunk)
                
                bytes_processed += original_size
                
                if progress and bytes_processed % (10 * 1024 * 1024) == 0:  # Every 10MB
                    elapsed = time.perf_counter() - start_time
                    throughput = bytes_processed / (1024 * 1024 * elapsed)
                    percent = (bytes_processed / file_size) * 100
                    print(f"  Progress: {percent:.1f}% ({throughput:.1f} MB/s)")
        
        elapsed = time.perf_counter() - start_time
        throughput = file_size / (1024 * 1024 * elapsed)
        
        if progress:
            print(f"✅ JIT file encrypted in {elapsed:.2f}s ({throughput:.1f} MB/s)")
        
        metadata = EncryptionMetadata(
            version='faro_cipher_jit_v1.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=read_chunk_size,
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            chunk_sizes=chunk_sizes
        )
        
        return metadata
    
    def benchmark_operations(self, data_size: int = 1024*1024) -> Dict[str, float]:
        """
        Benchmark JIT vs standard operations
        
        Args:
            data_size: Size of test data in bytes
            
        Returns:
            Dictionary with benchmark results
        """
        import os
        
        test_data = os.urandom(data_size)
        
        print(f"🏁 JIT Benchmark ({data_size//1024}KB test data):")
        
        # Benchmark JIT version
        start_time = time.perf_counter()
        jit_encrypted = self.encrypt(test_data)
        jit_encrypt_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        jit_decrypted = self.decrypt(jit_encrypted)
        jit_decrypt_time = time.perf_counter() - start_time
        
        # Verify correctness
        assert jit_decrypted == test_data, "JIT round-trip failed!"
        
        # Benchmark standard version
        standard_cipher = FaroCipher(self.key, self.profile, self.chunk_size, self.rounds)
        
        start_time = time.perf_counter()
        std_encrypted = standard_cipher.encrypt(test_data)
        std_encrypt_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        std_decrypted = standard_cipher.decrypt(std_encrypted)
        std_decrypt_time = time.perf_counter() - start_time
        
        # Verify correctness
        assert std_decrypted == test_data, "Standard round-trip failed!"
        
        # Calculate speedups
        encrypt_speedup = std_encrypt_time / jit_encrypt_time
        decrypt_speedup = std_decrypt_time / jit_decrypt_time
        
        jit_encrypt_throughput = data_size / (1024 * 1024 * jit_encrypt_time)
        jit_decrypt_throughput = data_size / (1024 * 1024 * jit_decrypt_time)
        std_encrypt_throughput = data_size / (1024 * 1024 * std_encrypt_time)
        std_decrypt_throughput = data_size / (1024 * 1024 * std_decrypt_time)
        
        results = {
            'jit_encrypt_time': jit_encrypt_time,
            'jit_decrypt_time': jit_decrypt_time,
            'std_encrypt_time': std_encrypt_time,
            'std_decrypt_time': std_decrypt_time,
            'encrypt_speedup': encrypt_speedup,
            'decrypt_speedup': decrypt_speedup,
            'jit_encrypt_throughput': jit_encrypt_throughput,
            'jit_decrypt_throughput': jit_decrypt_throughput,
            'std_encrypt_throughput': std_encrypt_throughput,
            'std_decrypt_throughput': std_decrypt_throughput
        }
        
        print(f"  📊 Encryption:")
        print(f"    JIT: {jit_encrypt_time:.3f}s ({jit_encrypt_throughput:.1f} MB/s)")
        print(f"    Standard: {std_encrypt_time:.3f}s ({std_encrypt_throughput:.1f} MB/s)")
        print(f"    🚀 Speedup: {encrypt_speedup:.1f}x")
        
        print(f"  📊 Decryption:")
        print(f"    JIT: {jit_decrypt_time:.3f}s ({jit_decrypt_throughput:.1f} MB/s)")
        print(f"    Standard: {std_decrypt_time:.3f}s ({std_decrypt_throughput:.1f} MB/s)")
        print(f"    🚀 Speedup: {decrypt_speedup:.1f}x")
        
        return results 