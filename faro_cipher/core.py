"""
Faro Cipher Core Implementation
==============================

Main cipher class providing a clean, professional interface
for the Faro Cipher encryption system.

License: WTFPL v2 - Do whatever you want with this code.
SPDX-License-Identifier: WTFPL
"""

import hashlib
import numpy as np
from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass

from .utils import pad_to_power_of_2, generate_key_fingerprint, verify_key_compatibility
from .shuffles import faro_shuffle, inverse_faro_shuffle, RELIABLE_SHUFFLE_VARIANTS
from .transforms import AVAILABLE_TRANSFORMS

@dataclass
class EncryptionMetadata:
    """Metadata for encrypted data"""
    version: str
    profile: str
    rounds: int
    chunk_size: int
    round_structure: List[Dict[str, Any]]
    key_fingerprint: str
    original_size: Optional[int] = None
    chunk_sizes: Optional[List[int]] = None

class SecurityProfile:
    """Security profile definitions for different use cases"""
    
    @staticmethod
    def performance() -> Dict[str, Any]:
        """High performance, basic security"""
        return {
            'rounds': 3,
            'emphasis_transforms': ['enhanced_xor', 'invert', 'swap_pairs'],
            'description': 'Fast encryption for non-sensitive data'
        }
    
    @staticmethod
    def balanced() -> Dict[str, Any]:
        """Balanced security and performance"""
        return {
            'rounds': 6,
            'emphasis_transforms': ['avalanche_cascade', 'enhanced_xor', 'fibonacci'],
            'description': 'Good balance of security and speed'
        }
    
    @staticmethod
    def maximum() -> Dict[str, Any]:
        """Maximum security, slower performance"""
        return {
            'rounds': 12,
            'emphasis_transforms': ['avalanche_cascade', 'prime_sieve', 'fibonacci'],
            'description': 'Maximum security for sensitive data'
        }

class FaroCipher:
    """
    Faro Cipher - High-Performance File Encryption
    
    A high-performance encryption system based on Faro shuffles and bit transforms.
    Uses only verified reliable shuffle variants for maximum stability.
    
    Example usage:
        cipher = FaroCipher(key=b"secret-key", profile="balanced")
        encrypted = cipher.encrypt(data)
        decrypted = cipher.decrypt(encrypted)
    """
    
    def __init__(self, key: bytes, profile: str = "balanced", chunk_size: int = 8192, rounds: Optional[int] = None):
        """
        Initialize Faro Cipher
        
        Args:
            key: Encryption key
            profile: Security profile ('performance', 'balanced', 'maximum') 
            chunk_size: Size of chunks for file processing
            rounds: Custom number of rounds (overrides profile default)
        """
        self.key = key
        self.chunk_size = chunk_size
        
        # Get profile configuration
        if profile == "performance":
            config = SecurityProfile.performance()
        elif profile == "balanced":
            config = SecurityProfile.balanced()
        elif profile == "maximum":
            config = SecurityProfile.maximum()
        else:
            raise ValueError(f"Unknown profile: {profile}")
        
        # Allow custom round count to override profile
        self.rounds = rounds if rounds is not None else config['rounds']
        self.profile = profile if rounds is None else f"custom-{self.rounds}"
        self.description = config['description'] if rounds is None else f"Custom {self.rounds}-round configuration"
        self.emphasis_transforms = config['emphasis_transforms']
        
        # Validate rounds
        if self.rounds < 1:
            raise ValueError("Rounds must be at least 1")
        if self.rounds > 100:
            raise ValueError("Maximum 100 rounds supported")
            
        # Generate key fingerprint and round structure
        self.key_fingerprint = generate_key_fingerprint(key)
        self.round_structure = self._generate_optimized_round_structure()
        
        # Print initialization info
        self._print_initialization_info()
    
    def _print_initialization_info(self):
        """Print cipher initialization information"""
        print("Faro Cipher Initialized")
        print(f"Profile: {self.profile} ({self.description})")
        print(f"Rounds: {self.rounds}")
        print(f"Chunk size: {self.chunk_size} bytes")
        print(f"Key fingerprint: {self.key_fingerprint}")
        
        # Count usage statistics
        shuffle_counts = {}
        transform_counts = {}
        chunk_size_counts = {}
        
        for round_info in self.round_structure:
            shuffle_type = round_info['shuffle_type']
            transform_type = round_info['transform_type']
            chunk_size = round_info['round_chunk_size']
            
            shuffle_counts[shuffle_type] = shuffle_counts.get(shuffle_type, 0) + 1
            transform_counts[transform_type] = transform_counts.get(transform_type, 0) + 1
            chunk_size_counts[chunk_size] = chunk_size_counts.get(chunk_size, 0) + 1
        
        print(f"Shuffles: {shuffle_counts}")
        print(f"Transforms: {transform_counts}")
        print(f"Chunk sizes: {self._format_chunk_sizes(chunk_size_counts)}")
    
    def _format_chunk_sizes(self, chunk_size_counts: Dict[int, int]) -> str:
        """Format chunk size counts in a readable way"""
        formatted = {}
        for size, count in chunk_size_counts.items():
            if size >= 1024:
                key = f"{size//1024}KB"
            else:
                key = f"{size}B"
            formatted[key] = count
        return str(formatted)
    
    def _generate_optimized_round_structure(self) -> List[Dict[str, Any]]:
        """Generate optimized round structure that maximizes entropy"""
        # Use PBKDF2 with round-dependent iterations for better key material
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            self.key,
            b'FaroCipherEntropy2024',
            10000 + (self.rounds * 1000),  # Scale iterations with rounds
            max(64, self.rounds * 8)  # More key material for more rounds
        )
        
        # Create multiple RNG states for different aspects
        master_seed = int.from_bytes(key_material[:4], 'big') % (2**32)
        shuffle_rng = np.random.RandomState(seed=master_seed)
        transform_rng = np.random.RandomState(seed=(master_seed + 1) % (2**32))
        param_rng = np.random.RandomState(seed=(master_seed + 2) % (2**32))
        
        structure = []
        
        # Get all available options
        shuffle_types = list(RELIABLE_SHUFFLE_VARIANTS.keys())
        transform_types = list(AVAILABLE_TRANSFORMS.keys())
        
        # Track usage to ensure good distribution
        shuffle_usage = {stype: 0 for stype in shuffle_types}
        transform_usage = {ttype: 0 for ttype in transform_types}
        
        for round_num in range(self.rounds):
            # Entropy-aware shuffle selection
            if round_num < len(shuffle_types):
                # Early rounds: ensure each shuffle type gets used
                available_shuffles = [s for s in shuffle_types if shuffle_usage[s] == min(shuffle_usage.values())]
                shuffle_type = shuffle_rng.choice(available_shuffles)
            else:
                # Later rounds: weighted selection based on usage
                weights = [1.0 / (1 + shuffle_usage[s]) for s in shuffle_types]
                weights = np.array(weights) / np.sum(weights)
                shuffle_type = shuffle_rng.choice(shuffle_types, p=weights)
            
            shuffle_usage[shuffle_type] += 1
            
            # Select variant from reliable options
            shuffle_variant = shuffle_rng.choice(RELIABLE_SHUFFLE_VARIANTS[shuffle_type])
            
            # Variable shuffle steps based on round position and entropy
            if round_num < 3:
                shuffle_steps = param_rng.choice([1, 2, 3], p=[0.5, 0.3, 0.2])  # Early rounds lighter
            elif round_num < self.rounds - 3:
                shuffle_steps = param_rng.choice([1, 2, 3, 4], p=[0.2, 0.3, 0.3, 0.2])  # Middle rounds balanced
            else:
                shuffle_steps = param_rng.choice([2, 3, 4], p=[0.3, 0.4, 0.3])  # Final rounds heavier
            
            # Entropy-aware transform selection
            if round_num < len(self.emphasis_transforms):
                # Use emphasis transforms early
                transform_type = self.emphasis_transforms[round_num % len(self.emphasis_transforms)]
            elif round_num < len(transform_types):
                # Ensure each transform gets used
                available_transforms = [t for t in transform_types if transform_usage[t] == min(transform_usage.values())]
                transform_type = transform_rng.choice(available_transforms)
            else:
                # Weighted selection for later rounds
                weights = [1.0 / (1 + transform_usage[t]) for t in transform_types]
                weights = np.array(weights) / np.sum(weights)
                transform_type = transform_rng.choice(transform_types, p=weights)
            
            transform_usage[transform_type] += 1
            
            # Generate diverse transform keys using round-specific seeds
            round_seed = int.from_bytes(
                key_material[(round_num * 4) % len(key_material):((round_num * 4) + 4) % len(key_material)], 
                'big'
            )
            round_rng = np.random.RandomState(seed=round_seed % (2**32))
            
            # Transform key based on transform type and round position
            if transform_type in ['enhanced_xor', 'invert', 'bit_flip']:
                transform_key = round_rng.randint(1000, 50000)  # Larger range for bit operations
            elif transform_type in ['avalanche_cascade', 'prime_sieve']:
                transform_key = round_rng.randint(2000, 100000)  # Even larger for complex transforms
            else:
                transform_key = round_rng.randint(1500, 75000)  # Medium range for others
            
            # Variable chunk size selection for multi-scale diffusion
            chunk_size = self._select_chunk_size_for_round(round_num, round_rng)
            
            structure.append({
                'shuffle_type': shuffle_type,
                'shuffle_variant': shuffle_variant,
                'shuffle_steps': shuffle_steps,
                'transform_type': transform_type,
                'transform_key': transform_key,
                'round_seed': round_seed,
                'round_chunk_size': chunk_size,
                'entropy_score': self._calculate_round_entropy(shuffle_type, shuffle_variant, transform_type, chunk_size)
            })
        
        # Calculate total entropy score
        total_entropy = sum(round_info['entropy_score'] for round_info in structure)
        
        # Add entropy info to structure
        for round_info in structure:
            round_info['total_entropy'] = total_entropy
            
        return structure
    
    def _select_chunk_size_for_round(self, round_num: int, rng: np.random.RandomState) -> int:
        """Select optimal chunk size for this round based on diffusion strategy"""
        # Available power-of-2 chunk sizes (in bytes)
        chunk_sizes = [
            1024,   # 1KB  - Ultra fine-grained  
            2048,   # 2KB  - Fine-grained
            4096,   # 4KB  - Small scale
            8192,   # 8KB  - Standard scale (current default)
            16384,  # 16KB - Medium cross-chunk
            32768,  # 32KB - Large cross-chunk  
            65536   # 64KB - Maximum diffusion
        ]
        
        # Strategy based on round position for optimal diffusion
        if round_num < 3:
            # Early rounds: Mix of fine and standard
            return rng.choice([2048, 4096, 8192], p=[0.2, 0.3, 0.5])
            
        elif round_num < self.rounds // 3:
            # First third: Introduce cross-chunk mixing
            return rng.choice([4096, 8192, 16384], p=[0.2, 0.4, 0.4])
            
        elif round_num < 2 * self.rounds // 3:
            # Middle third: Maximum cross-chunk diffusion
            return rng.choice([8192, 16384, 32768], p=[0.3, 0.4, 0.3])
            
        elif round_num < self.rounds - 3:
            # Final third: Back to smaller chunks for fine-tuning
            return rng.choice([2048, 4096, 8192, 16384], p=[0.2, 0.3, 0.3, 0.2])
            
        else:
            # Final rounds: Standard chunking for stability
            return rng.choice([4096, 8192], p=[0.3, 0.7])
    
    def _calculate_round_entropy(self, shuffle_type: str, shuffle_variant: int, transform_type: str, chunk_size: int) -> float:
        """Calculate entropy score for a round configuration"""
        # Base entropy from shuffle type complexity
        shuffle_entropy = {
            'none': 1.0,
            'in': 3.0,
            'out': 3.0, 
            'milk': 2.5,
            'cut': 2.0
        }
        
        # Transform entropy based on complexity
        transform_entropy = {
            'enhanced_xor': 2.0,
            'invert': 1.5,
            'swap_pairs': 2.5,
            'bit_flip': 2.0,
            'fibonacci': 4.0,
            'avalanche_cascade': 5.0,
            'prime_sieve': 4.5
        }
        
        # Chunk size entropy factor (larger chunks = more cross-diffusion)
        chunk_entropy_factor = {
            1024: 1.0,   # 1KB
            2048: 1.2,   # 2KB  
            4096: 1.5,   # 4KB
            8192: 2.0,   # 8KB (baseline)
            16384: 2.8,  # 16KB
            32768: 3.5,  # 32KB
            65536: 4.0   # 64KB
        }
        
        # Variant adds small amount
        variant_entropy = shuffle_variant * 0.1
        
        base_entropy = shuffle_entropy.get(shuffle_type, 2.0) + transform_entropy.get(transform_type, 2.0) + variant_entropy
        chunk_factor = chunk_entropy_factor.get(chunk_size, 2.0)
        
        return base_entropy * chunk_factor
    
    def _process_data_variable_chunks(self, data: bytes, encrypt: bool = True) -> bytes:
        """Process data using variable chunk sizes per round"""
        
        # Find the maximum chunk size across all rounds
        max_chunk_size = max(round_info['round_chunk_size'] for round_info in self.round_structure)
        
        # For encryption: pad data to be divisible by max chunk size at the start
        # For decryption: the data should already be properly sized from encryption
        original_length = len(data)
        current_data = data
        
        if encrypt:
            # Pad to multiple of max chunk size
            padding_needed = (max_chunk_size - (len(data) % max_chunk_size)) % max_chunk_size
            if padding_needed > 0:
                # Use deterministic padding based on data content for consistency
                padding_byte = (sum(data) % 256) if data else 0
                current_data = data + bytes([padding_byte] * padding_needed)
        
        # Apply rounds
        if encrypt:
            # Forward processing: apply rounds in order
            for round_num, round_info in enumerate(self.round_structure):
                current_data = self._apply_round_to_data(current_data, round_info, encrypt=True, round_num=round_num)
        else:
            # Reverse processing: apply rounds in reverse order
            for round_num, round_info in enumerate(reversed(self.round_structure)):
                current_data = self._apply_round_to_data(current_data, round_info, encrypt=False, round_num=len(self.round_structure)-1-round_num)
        
        # For decryption: trim back to original length (stored in metadata)
        # Note: original_length will be passed through metadata during decryption
        
        return current_data
    
    def _apply_round_to_data(self, data: bytes, round_info: Dict[str, Any], encrypt: bool, round_num: int) -> bytes:
        """Apply a single round with its specific chunk size to the entire data"""
        chunk_size = round_info['round_chunk_size']
        
        # Split data into chunks of this round's size
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        
        # Process each chunk with this round's parameters
        processed_chunks = []
        for chunk in chunks:
            processed_chunk = self._process_single_chunk(chunk, round_info, encrypt)
            processed_chunks.append(processed_chunk)
        
        # Recombine chunks
        return b''.join(processed_chunks)
    
    def _process_single_chunk(self, chunk: bytes, round_info: Dict[str, Any], encrypt: bool) -> bytes:
        """Process a single chunk through one round of shuffling and transforms"""
        if len(chunk) == 0:
            return chunk
            
        # Convert to bits
        bits = np.unpackbits(np.frombuffer(chunk, dtype=np.uint8))
        
        if encrypt:
            # Pad to power of 2 for encryption
            padded_bits, original_bit_length = pad_to_power_of_2(bits)
            current_bits = padded_bits.copy()
            
            # Apply shuffle
            if round_info['shuffle_type'] != 'none':
                current_bits = faro_shuffle(
                    current_bits,
                    round_info['shuffle_type'],
                    round_info['shuffle_steps'],
                    round_info['shuffle_variant']
                )
            
            # Apply transform
            transform_func = AVAILABLE_TRANSFORMS[round_info['transform_type']]
            current_bits = transform_func(current_bits, round_info['transform_key'])
            
            # Convert back to bytes (keep full padded result for encryption)
            result_bytes = np.packbits(current_bits).tobytes()
            
        else:
            # For decryption: encrypted data is already the correct size
            # No padding needed - the bits are already in power-of-2 format from encryption
            current_bits = bits.copy()
            
            # Apply inverse transform
            transform_func = AVAILABLE_TRANSFORMS[round_info['transform_type']]
            current_bits = transform_func(current_bits, round_info['transform_key'])
            
            # Apply inverse shuffle
            if round_info['shuffle_type'] != 'none':
                current_bits = inverse_faro_shuffle(
                    current_bits,
                    round_info['shuffle_type'],
                    round_info['shuffle_steps'],
                    round_info['shuffle_variant']
                )
            
            # Convert back to bytes and trim to match input chunk size
            result_bytes = np.packbits(current_bits).tobytes()
            
            # Trim to match the original chunk size for this round
            if len(result_bytes) > len(chunk):
                result_bytes = result_bytes[:len(chunk)]
        
        return result_bytes
    
    def encrypt(self, data: Union[bytes, str]) -> Dict[str, Any]:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt (bytes or string)
            
        Returns:
            Dictionary with 'encrypted_data' and 'metadata'
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self._process_data_variable_chunks(data, encrypt=True)
        
        metadata = EncryptionMetadata(
            version='faro_cipher_v1.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=self.chunk_size,
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            original_size=len(data)
        )
        
        return {
            'encrypted_data': encrypted_data,
            'metadata': metadata
        }
    
    def decrypt(self, encrypted_result: Dict[str, Any]) -> bytes:
        """
        Decrypt data
        
        Args:
            encrypted_result: Result from encrypt() method
            
        Returns:
            Decrypted data as bytes
        """
        encrypted_data = encrypted_result['encrypted_data']
        metadata = encrypted_result['metadata']
        
        # Verify key compatibility
        if not verify_key_compatibility(self.key, metadata.key_fingerprint):
            raise ValueError("Key fingerprint mismatch - wrong key or corrupted metadata")
        
        # Decrypt
        decrypted_data = self._process_data_variable_chunks(encrypted_data, encrypt=False)
        
        # Trim to original size if specified
        if metadata.original_size is not None and len(decrypted_data) > metadata.original_size:
            decrypted_data = decrypted_data[:metadata.original_size]
        
        return decrypted_data
    
    def encrypt_file(self, input_file: str, output_file: str) -> EncryptionMetadata:
        """
        Encrypt a file using variable chunk sizes
        
        Args:
            input_file: Path to input file
            output_file: Path to output encrypted file
            
        Returns:
            Encryption metadata
        """
        # Find the maximum chunk size needed across all rounds
        max_chunk_size = max(round_info['round_chunk_size'] for round_info in self.round_structure)
        
        chunk_sizes = []
        
        with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
            while True:
                # Read data in max chunk size to ensure we can handle any round's requirements
                data_chunk = infile.read(max_chunk_size)
                if not data_chunk:
                    break
                
                original_size = len(data_chunk)
                encrypted_chunk = self._process_data_variable_chunks(data_chunk, encrypt=True)
                
                # Store chunk metadata and data
                chunk_sizes.append(original_size)
                outfile.write(len(encrypted_chunk).to_bytes(4, 'big'))
                outfile.write(encrypted_chunk)
        
        metadata = EncryptionMetadata(
            version='faro_cipher_v1.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=max_chunk_size,  # Store max chunk size for reference
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            chunk_sizes=chunk_sizes
        )
        
        return metadata
    
    def decrypt_file(self, input_file: str, output_file: str, metadata: EncryptionMetadata) -> bool:
        """
        Decrypt a file
        
        Args:
            input_file: Path to encrypted file
            output_file: Path to output decrypted file
            metadata: Encryption metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify key
            if not verify_key_compatibility(self.key, metadata.key_fingerprint):
                print("❌ Key fingerprint mismatch!")
                return False
            
            with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                for original_size in metadata.chunk_sizes:
                    # Read chunk length
                    chunk_len_bytes = infile.read(4)
                    if len(chunk_len_bytes) != 4:
                        break
                    chunk_len = int.from_bytes(chunk_len_bytes, 'big')
                    
                    # Read encrypted chunk
                    encrypted_chunk = infile.read(chunk_len)
                    if len(encrypted_chunk) != chunk_len:
                        break
                    
                    # Decrypt and write
                    decrypted_chunk = self._process_data_variable_chunks(
                        encrypted_chunk,
                        encrypt=False
                    )
                    
                    # Trim to original size
                    if len(decrypted_chunk) > original_size:
                        decrypted_chunk = decrypted_chunk[:original_size]
                    
                    outfile.write(decrypted_chunk)
            
            return True
            
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get cipher configuration information"""
        return {
            'profile': self.profile,
            'description': self.description,
            'rounds': self.rounds,
            'chunk_size': self.chunk_size,
            'key_fingerprint': self.key_fingerprint,
            'shuffle_variants_used': len([r for r in self.round_structure if r['shuffle_type'] != 'none']),
            'total_shuffle_variants_available': sum(len(variants) for variants in RELIABLE_SHUFFLE_VARIANTS.values()),
            'transforms_available': len(AVAILABLE_TRANSFORMS)
        } 