"""
Faro Cipher Core
================
Single cipher class built on byte-level faro shuffles and self-inverse transforms.
The byte-level approach avoids bit-expansion (np.unpackbits/packbits), giving an
8x reduction in memory usage and a corresponding speed improvement.

License: WTFPL v2
"""

import hashlib
import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .shuffles import shuffle, inverse_shuffle, RELIABLE_SHUFFLE_VARIANTS
from .transforms import AVAILABLE_TRANSFORMS
from .utils import generate_key_fingerprint, verify_key_compatibility

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EncryptionMetadata:
    version: str
    profile: str
    rounds: int
    chunk_size: int
    round_structure: List[Dict[str, Any]]
    key_fingerprint: str
    original_size: Optional[int] = None
    chunk_sizes: Optional[List[int]] = field(default=None)


class SecurityProfile:
    """Preset round counts and transform emphasis per security level."""

    PROFILES = {
        'performance': {
            'rounds': 3,
            'emphasis': ['enhanced_xor', 'invert', 'swap_pairs'],
            'description': 'Fast encryption for non-sensitive data',
        },
        'balanced': {
            'rounds': 6,
            'emphasis': ['avalanche_cascade', 'enhanced_xor', 'fibonacci'],
            'description': 'Good balance of security and speed',
        },
        'maximum': {
            'rounds': 12,
            'emphasis': ['avalanche_cascade', 'prime_sieve', 'fibonacci'],
            'description': 'Maximum security for sensitive data',
        },
    }

    @classmethod
    def get(cls, name: str) -> Dict[str, Any]:
        if name not in cls.PROFILES:
            raise ValueError(f"Unknown profile '{name}'. Choose from: {list(cls.PROFILES)}")
        return cls.PROFILES[name]


# ---------------------------------------------------------------------------
# Cipher
# ---------------------------------------------------------------------------

# All chunk sizes used in round structure selection — must all be powers of 2
# and divisors of the largest value so that padding works evenly.
_CHUNK_SIZES = [1024, 2048, 4096, 8192, 16384, 32768, 65536]
_MAX_CHUNK_SIZE = max(_CHUNK_SIZES)


class FaroCipher:
    """
    Faro Cipher — encryption via repeated faro shuffles and bit transforms.

    Example::

        cipher = FaroCipher(key=b"secret", profile="balanced")
        result = cipher.encrypt(b"Hello, world!")
        plain  = cipher.decrypt(result)
        assert plain == b"Hello, world!"
    """

    def __init__(
        self,
        key: bytes,
        profile: str = "balanced",
        rounds: Optional[int] = None,
    ) -> None:
        config = SecurityProfile.get(profile)

        self.key = key
        self.profile = profile if rounds is None else f"custom-{rounds}"
        self.rounds = rounds if rounds is not None else config['rounds']
        self._description = config['description'] if rounds is None else f"Custom {self.rounds}-round configuration"
        self._emphasis = config['emphasis']
        self.key_fingerprint = generate_key_fingerprint(key)

        if not 1 <= self.rounds <= 100:
            raise ValueError("Rounds must be between 1 and 100")

        self.round_structure = self._build_round_structure()
        self.chunk_size = _MAX_CHUNK_SIZE  # exposed for metadata compatibility

        log.debug(
            "FaroCipher initialised: profile=%s rounds=%d key=%s",
            self.profile, self.rounds, self.key_fingerprint,
        )

    # ------------------------------------------------------------------
    # Round structure generation
    # ------------------------------------------------------------------

    def _build_round_structure(self) -> List[Dict[str, Any]]:
        """Derive a deterministic round structure from the key via PBKDF2."""
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            self.key,
            b'FaroCipherEntropy2024',
            10000 + self.rounds * 1000,
            max(64, self.rounds * 8),
        )
        seed = int.from_bytes(key_material[:4], 'big') % (2 ** 32)
        shuffle_rng   = np.random.RandomState(seed)
        transform_rng = np.random.RandomState(seed + 1)
        param_rng     = np.random.RandomState(seed + 2)

        shuffle_types    = list(RELIABLE_SHUFFLE_VARIANTS.keys())
        transform_types  = list(AVAILABLE_TRANSFORMS.keys())
        shuffle_usage    = {s: 0 for s in shuffle_types}
        transform_usage  = {t: 0 for t in transform_types}

        structure = []
        for round_num in range(self.rounds):

            # --- shuffle type: distribute evenly, then weight by least-used ---
            if round_num < len(shuffle_types):
                candidates = [s for s in shuffle_types if shuffle_usage[s] == min(shuffle_usage.values())]
                shuffle_type = shuffle_rng.choice(candidates)
            else:
                weights = np.array([1.0 / (1 + shuffle_usage[s]) for s in shuffle_types])
                shuffle_type = shuffle_rng.choice(shuffle_types, p=weights / weights.sum())
            shuffle_usage[shuffle_type] += 1

            shuffle_variant = int(shuffle_rng.choice(RELIABLE_SHUFFLE_VARIANTS[shuffle_type]))

            # --- shuffle steps scaled by round position ---
            if round_num < 3:
                steps = int(param_rng.choice([1, 2, 3], p=[0.5, 0.3, 0.2]))
            elif round_num < self.rounds - 3:
                steps = int(param_rng.choice([1, 2, 3, 4], p=[0.2, 0.3, 0.3, 0.2]))
            else:
                steps = int(param_rng.choice([2, 3, 4], p=[0.3, 0.4, 0.3]))

            # --- transform type: emphasis transforms first, then distribute ---
            if round_num < len(self._emphasis):
                transform_type = self._emphasis[round_num % len(self._emphasis)]
            elif round_num < len(transform_types):
                candidates = [t for t in transform_types if transform_usage[t] == min(transform_usage.values())]
                transform_type = transform_rng.choice(candidates)
            else:
                weights = np.array([1.0 / (1 + transform_usage[t]) for t in transform_types])
                transform_type = transform_rng.choice(transform_types, p=weights / weights.sum())
            transform_usage[transform_type] += 1

            # --- transform key derived from key_material ---
            km_offset = (round_num * 4) % len(key_material)
            round_seed = int.from_bytes(
                key_material[km_offset:km_offset + 4]
                if km_offset + 4 <= len(key_material)
                else key_material[km_offset:] + key_material[:4 - (len(key_material) - km_offset)],
                'big',
            )
            round_rng = np.random.RandomState(round_seed % (2 ** 32))
            if transform_type in ('enhanced_xor', 'invert', 'bit_flip'):
                transform_key = int(round_rng.randint(1000, 50000))
            elif transform_type in ('avalanche_cascade', 'prime_sieve'):
                transform_key = int(round_rng.randint(2000, 100000))
            else:
                transform_key = int(round_rng.randint(1500, 75000))

            # --- chunk size for multi-scale diffusion ---
            chunk_size = self._pick_chunk_size(round_num, round_rng)

            structure.append({
                'shuffle_type':    shuffle_type,
                'shuffle_variant': shuffle_variant,
                'shuffle_steps':   steps,
                'transform_type':  transform_type,
                'transform_key':   transform_key,
                'round_chunk_size': chunk_size,
            })

        return structure

    def _pick_chunk_size(self, round_num: int, rng: np.random.RandomState) -> int:
        """Choose a chunk size that maximises diffusion at each stage."""
        third = self.rounds // 3
        if round_num < 3:
            return int(rng.choice([2048, 4096, 8192], p=[0.2, 0.3, 0.5]))
        elif round_num < third:
            return int(rng.choice([4096, 8192, 16384], p=[0.2, 0.4, 0.4]))
        elif round_num < 2 * third:
            return int(rng.choice([8192, 16384, 32768], p=[0.3, 0.4, 0.3]))
        elif round_num < self.rounds - 3:
            return int(rng.choice([2048, 4096, 8192, 16384], p=[0.2, 0.3, 0.3, 0.2]))
        else:
            return int(rng.choice([4096, 8192], p=[0.3, 0.7]))

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    def _process(self, data: bytes, encrypt: bool) -> bytes:
        """Apply all rounds to *data* in forward (encrypt) or reverse (decrypt) order."""
        arr = np.frombuffer(data, dtype=np.uint8).copy()
        rounds = self.round_structure if encrypt else list(reversed(self.round_structure))

        for r in rounds:
            chunk_size = r['round_chunk_size']
            out = np.empty_like(arr)
            for start in range(0, len(arr), chunk_size):
                chunk = arr[start:start + chunk_size].copy()
                if encrypt:
                    chunk = AVAILABLE_TRANSFORMS[r['transform_type']](chunk, r['transform_key'])
                    chunk = shuffle(chunk, r['shuffle_type'], r['shuffle_steps'], r['shuffle_variant'])
                else:
                    chunk = inverse_shuffle(chunk, r['shuffle_type'], r['shuffle_steps'], r['shuffle_variant'])
                    chunk = AVAILABLE_TRANSFORMS[r['transform_type']](chunk, r['transform_key'])
                out[start:start + chunk_size] = chunk
            arr = out

        return arr.tobytes()

    @staticmethod
    def _pad(data: bytes) -> bytes:
        """Pad data to the nearest multiple of _MAX_CHUNK_SIZE."""
        needed = (-len(data)) % _MAX_CHUNK_SIZE
        if needed:
            pad_byte = sum(data) % 256 if data else 0
            data += bytes([pad_byte] * needed)
        return data

    # ------------------------------------------------------------------
    # Public API — in-memory
    # ------------------------------------------------------------------

    def encrypt(self, data: Union[bytes, str]) -> Dict[str, Any]:
        """Encrypt *data* and return a dict with ``encrypted_data`` and ``metadata``."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        original_size = len(data)
        encrypted = self._process(self._pad(data), encrypt=True)
        return {
            'encrypted_data': encrypted,
            'metadata': EncryptionMetadata(
                version='faro_cipher_v2.0',
                profile=self.profile,
                rounds=self.rounds,
                chunk_size=self.chunk_size,
                round_structure=self.round_structure,
                key_fingerprint=self.key_fingerprint,
                original_size=original_size,
            ),
        }

    def decrypt(self, encrypted_result: Dict[str, Any]) -> bytes:
        """Decrypt a result produced by :meth:`encrypt`."""
        metadata = encrypted_result['metadata']
        if not verify_key_compatibility(self.key, metadata.key_fingerprint):
            raise ValueError("Key fingerprint mismatch — wrong key or corrupted metadata")
        decrypted = self._process(encrypted_result['encrypted_data'], encrypt=False)
        if metadata.original_size is not None:
            decrypted = decrypted[:metadata.original_size]
        return decrypted

    # ------------------------------------------------------------------
    # Public API — file I/O
    # ------------------------------------------------------------------

    def encrypt_file(self, input_path: str, output_path: str) -> EncryptionMetadata:
        """Encrypt *input_path* and write the result to *output_path*.

        Each ``_MAX_CHUNK_SIZE``-byte block is encrypted independently. A 4-byte
        big-endian length prefix is written before each encrypted block so that
        :meth:`decrypt_file` can reassemble the plaintext exactly.
        """
        chunk_sizes = []
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            while True:
                raw = fin.read(_MAX_CHUNK_SIZE)
                if not raw:
                    break
                chunk_sizes.append(len(raw))
                enc = self._process(self._pad(raw), encrypt=True)
                fout.write(len(enc).to_bytes(4, 'big'))
                fout.write(enc)

        return EncryptionMetadata(
            version='faro_cipher_v2.0',
            profile=self.profile,
            rounds=self.rounds,
            chunk_size=_MAX_CHUNK_SIZE,
            round_structure=self.round_structure,
            key_fingerprint=self.key_fingerprint,
            chunk_sizes=chunk_sizes,
        )

    def decrypt_file(self, input_path: str, output_path: str, metadata: EncryptionMetadata) -> bool:
        """Decrypt *input_path* using *metadata* and write plaintext to *output_path*.

        Returns ``True`` on success, ``False`` on failure.
        """
        if not verify_key_compatibility(self.key, metadata.key_fingerprint):
            print("Key fingerprint mismatch — wrong key or corrupted metadata")
            return False
        try:
            with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
                for original_size in metadata.chunk_sizes:
                    length_bytes = fin.read(4)
                    if len(length_bytes) != 4:
                        break
                    enc_chunk = fin.read(int.from_bytes(length_bytes, 'big'))
                    dec = self._process(enc_chunk, encrypt=False)
                    fout.write(dec[:original_size])
            return True
        except Exception as exc:
            print(f"Decryption failed: {exc}")
            return False

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    def get_info(self) -> Dict[str, Any]:
        """Return a summary of the cipher configuration."""
        return {
            'profile':     self.profile,
            'description': self._description,
            'rounds':      self.rounds,
            'chunk_size':  self.chunk_size,
            'key_fingerprint': self.key_fingerprint,
            'shuffle_types_available': list(RELIABLE_SHUFFLE_VARIANTS.keys()),
            'transforms_available':    list(AVAILABLE_TRANSFORMS.keys()),
        }
