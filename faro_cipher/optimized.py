"""
Faro Cipher Optimized Implementation
===================================

High-performance version with memory pooling, chunk batching, and multithreading.
"""

import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Union, Optional, Tuple
from queue import Queue
import time

from .core import FaroCipher, EncryptionMetadata
from .utils import pad_to_power_of_2
from .shuffles import faro_shuffle, inverse_faro_shuffle
from .transforms import AVAILABLE_TRANSFORMS

class MemoryPool:
    """Thread-safe memory pool for reusing numpy arrays"""
    
    def __init__(self, max_pool_size: int = 100):
        self.pools = {}  # size -> list of arrays
        self.max_pool_size = max_pool_size
        self.lock = threading.Lock()
    
    def get_array(self, size: int, dtype=np.uint8) -> np.ndarray:
        """Get a reusable array of specified size"""
        with self.lock:
            pool_key = (size, dtype)
            if pool_key in self.pools and self.pools[pool_key]:
                array = self.pools[pool_key].pop()
                array.fill(0)  # Clear previous data
                return array
            
        # Create new array if pool is empty
        return np.zeros(size, dtype=dtype)
    
    def return_array(self, array: np.ndarray):
        """Return array to pool for reuse"""
        if array is None:
            return
            
        with self.lock:
            pool_key = (len(array), array.dtype)
            if pool_key not in self.pools:
                self.pools[pool_key] = []
            
            if len(self.pools[pool_key]) < self.max_pool_size:
                self.pools[pool_key].append(array)
    
    def clear(self):
        """Clear all pools"""
        with self.lock:
            self.pools.clear()

class ChunkBatch:
    """Represents a batch of chunks to process together"""
    
    def __init__(self, chunks: List[bytes], chunk_indices: List[int]):
        self.chunks = chunks
        self.chunk_indices = chunk_indices
        self.processed_chunks = [None] * len(chunks)

class OptimizedFaroCipher(FaroCipher):
    """
    Optimized Faro Cipher with batching, memory pooling, and multithreading
    """
    
    def __init__(self, key: bytes, profile: str = "balanced", chunk_size: int = 8192, 
                 rounds: Optional[int] = None, num_threads: int = 4, batch_size: int = 16):
        """
        Initialize optimized cipher
        
        Args:
            key: Encryption key
            profile: Security profile
            chunk_size: Base chunk size
            rounds: Number of rounds
            num_threads: Number of worker threads
            batch_size: Number of chunks to process in each batch
        """
        super().__init__(key, profile, chunk_size, rounds)
        self.num_threads = max(1, min(num_threads, 16))  # Reasonable bounds
        self.batch_size = max(1, min(batch_size, 32))    # Reasonable bounds
        self.memory_pool = MemoryPool()
        
        print(f"⚡ Optimized Mode: {self.num_threads} threads, {self.batch_size} batch size")
    
    def _process_chunks_batch(self, batch: ChunkBatch, round_info: Dict[str, Any], 
                            encrypt: bool) -> ChunkBatch:
        """Process a batch of chunks together for better performance"""
        
        for i, chunk in enumerate(batch.chunks):
            if len(chunk) == 0:
                batch.processed_chunks[i] = chunk
                continue
            
            # Use memory pool for bit arrays
            bits = np.unpackbits(np.frombuffer(chunk, dtype=np.uint8))
            
            if encrypt:
                # Pad to power of 2 for encryption
                padded_bits, _ = pad_to_power_of_2(bits)
                current_bits = self.memory_pool.get_array(len(padded_bits))
                current_bits[:len(padded_bits)] = padded_bits
                
                # Apply shuffle
                if round_info['shuffle_type'] != 'none':
                    shuffled_bits = self.memory_pool.get_array(len(current_bits))
                    shuffled_bits[:] = faro_shuffle(
                        current_bits[:len(padded_bits)],
                        round_info['shuffle_type'],
                        round_info['shuffle_steps'],
                        round_info['shuffle_variant']
                    )
                    self.memory_pool.return_array(current_bits)
                    current_bits = shuffled_bits
                
                # Apply transform
                transform_func = AVAILABLE_TRANSFORMS[round_info['transform_type']]
                transform_func(current_bits[:len(padded_bits)], round_info['transform_key'])
                
                # Convert back to bytes
                result_bytes = np.packbits(current_bits[:len(padded_bits)]).tobytes()
                self.memory_pool.return_array(current_bits)
                
            else:
                # For decryption: use bits as-is (already correct size from encryption)
                current_bits = self.memory_pool.get_array(len(bits))
                current_bits[:len(bits)] = bits
                
                # Apply inverse transform
                transform_func = AVAILABLE_TRANSFORMS[round_info['transform_type']]
                transform_func(current_bits[:len(bits)], round_info['transform_key'])
                
                # Apply inverse shuffle
                if round_info['shuffle_type'] != 'none':
                    shuffled_bits = self.memory_pool.get_array(len(current_bits))
                    shuffled_bits[:len(bits)] = inverse_faro_shuffle(
                        current_bits[:len(bits)],
                        round_info['shuffle_type'],
                        round_info['shuffle_steps'],
                        round_info['shuffle_variant']
                    )
                    self.memory_pool.return_array(current_bits)
                    current_bits = shuffled_bits
                
                # Convert back to bytes and trim
                result_bytes = np.packbits(current_bits[:len(bits)]).tobytes()
                if len(result_bytes) > len(chunk):
                    result_bytes = result_bytes[:len(chunk)]
                    
                self.memory_pool.return_array(current_bits)
            
            batch.processed_chunks[i] = result_bytes
        
        return batch
    
    def _apply_round_to_data_optimized(self, data: bytes, round_info: Dict[str, Any], 
                                     encrypt: bool, round_num: int) -> bytes:
        """Apply a round with optimized batch processing and multithreading"""
        chunk_size = round_info['round_chunk_size']
        
        # Split data into chunks
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        
        # Group chunks into batches
        batches = []
        for i in range(0, len(chunks), self.batch_size):
            batch_chunks = chunks[i:i + self.batch_size]
            batch_indices = list(range(i, min(i + self.batch_size, len(chunks))))
            batches.append(ChunkBatch(batch_chunks, batch_indices))
        
        # Process batches in parallel
        processed_batches = [None] * len(batches)
        
        if self.num_threads == 1 or len(batches) == 1:
            # Single-threaded processing
            for i, batch in enumerate(batches):
                processed_batches[i] = self._process_chunks_batch(batch, round_info, encrypt)
        else:
            # Multi-threaded processing
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                future_to_index = {
                    executor.submit(self._process_chunks_batch, batch, round_info, encrypt): i
                    for i, batch in enumerate(batches)
                }
                
                for future in as_completed(future_to_index):
                    batch_index = future_to_index[future]
                    try:
                        processed_batches[batch_index] = future.result()
                    except Exception as e:
                        raise RuntimeError(f"Batch processing failed: {e}")
        
        # Recombine processed chunks
        result_chunks = []
        for batch in processed_batches:
            result_chunks.extend(batch.processed_chunks)
        
        return b''.join(result_chunks)
    
    def _process_data_variable_chunks_optimized(self, data: bytes, encrypt: bool = True) -> bytes:
        """Optimized data processing with batching and threading"""
        
        # Find the maximum chunk size across all rounds
        max_chunk_size = max(round_info['round_chunk_size'] for round_info in self.round_structure)
        
        # Pad data to be divisible by max chunk size at the start
        original_length = len(data)
        current_data = data
        
        if encrypt:
            # Pad to multiple of max chunk size
            padding_needed = (max_chunk_size - (len(data) % max_chunk_size)) % max_chunk_size
            if padding_needed > 0:
                # Use deterministic padding based on data content
                padding_byte = (sum(data) % 256) if data else 0
                current_data = data + bytes([padding_byte] * padding_needed)
        
        # Apply rounds with optimization
        if encrypt:
            # Forward processing
            for round_num, round_info in enumerate(self.round_structure):
                current_data = self._apply_round_to_data_optimized(
                    current_data, round_info, encrypt=True, round_num=round_num
                )
        else:
            # Reverse processing
            for round_num, round_info in enumerate(reversed(self.round_structure)):
                current_data = self._apply_round_to_data_optimized(
                    current_data, round_info, encrypt=False, 
                    round_num=len(self.round_structure)-1-round_num
                )
        
        return current_data
    
    def encrypt(self, data: Union[bytes, str]) -> Dict[str, Any]:
        """
        Optimized encryption with batching and threading
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        start_time = time.perf_counter()
        encrypted_data = self._process_data_variable_chunks_optimized(data, encrypt=True)
        encrypt_time = time.perf_counter() - start_time
        
        metadata = EncryptionMetadata(
            version='faro_cipher_optimized_v1.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=self.chunk_size,
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            original_size=len(data)
        )
        
        # Clear memory pool periodically to prevent memory leaks
        if len(self.memory_pool.pools) > 50:
            self.memory_pool.clear()
        
        throughput = len(data) / (1024 * 1024 * encrypt_time) if encrypt_time > 0 else 0
        print(f"⚡ Optimized encryption: {throughput:.1f} MB/s")
        
        return {
            'encrypted_data': encrypted_data,
            'metadata': metadata
        }
    
    def decrypt(self, encrypted_result: Dict[str, Any]) -> bytes:
        """
        Optimized decryption with batching and threading
        """
        encrypted_data = encrypted_result['encrypted_data']
        metadata = encrypted_result['metadata']
        
        # Verify key compatibility
        from .utils import verify_key_compatibility
        if not verify_key_compatibility(self.key, metadata.key_fingerprint):
            raise ValueError("Key fingerprint mismatch - wrong key or corrupted metadata")
        
        start_time = time.perf_counter()
        decrypted_data = self._process_data_variable_chunks_optimized(encrypted_data, encrypt=False)
        decrypt_time = time.perf_counter() - start_time
        
        # Trim to original size if specified
        if metadata.original_size is not None and len(decrypted_data) > metadata.original_size:
            decrypted_data = decrypted_data[:metadata.original_size]
        
        throughput = len(decrypted_data) / (1024 * 1024 * decrypt_time) if decrypt_time > 0 else 0
        print(f"⚡ Optimized decryption: {throughput:.1f} MB/s")
        
        return decrypted_data
    
    def encrypt_file_optimized(self, input_file: str, output_file: str, 
                             progress: bool = True) -> EncryptionMetadata:
        """
        Optimized file encryption with streaming and parallel processing
        """
        import os
        from pathlib import Path
        
        file_size = Path(input_file).stat().st_size
        max_chunk_size = max(round_info['round_chunk_size'] for round_info in self.round_structure)
        
        # Use larger read chunks for file I/O efficiency
        read_chunk_size = max(max_chunk_size * 8, 1024 * 1024)  # At least 1MB reads
        
        if progress:
            print(f"⚡ Optimized file encryption: {file_size//1024//1024}MB with {self.num_threads} threads")
        
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
                encrypted_chunk = self._process_data_variable_chunks_optimized(data_chunk, encrypt=True)
                
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
            print(f"✅ File encrypted in {elapsed:.2f}s ({throughput:.1f} MB/s)")
        
        metadata = EncryptionMetadata(
            version='faro_cipher_optimized_v1.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=read_chunk_size,
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            chunk_sizes=chunk_sizes
        )
        
        return metadata
    
    def __del__(self):
        """Cleanup memory pool on destruction"""
        if hasattr(self, 'memory_pool'):
            self.memory_pool.clear() 