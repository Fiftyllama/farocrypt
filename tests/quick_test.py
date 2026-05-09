#!/usr/bin/env python3
"""Quick round-trip test via file encrypt/decrypt."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from faro_cipher import FaroCipher


class QuickTest(unittest.TestCase):
    def test_file_round_trip(self):
        data = b'Hello, this is a test message for our cipher!'
        key = b'quick-test-key'
        cipher = FaroCipher(key=key, profile='performance')

        with tempfile.TemporaryDirectory() as tmp:
            plain_path = os.path.join(tmp, 'plain.bin')
            enc_path   = os.path.join(tmp, 'plain.enc')
            dec_path   = os.path.join(tmp, 'plain.dec')

            with open(plain_path, 'wb') as f:
                f.write(data)

            metadata = cipher.encrypt_file(plain_path, enc_path)
            ok = cipher.decrypt_file(enc_path, dec_path, metadata)
            self.assertTrue(ok)

            with open(dec_path, 'rb') as f:
                decrypted = f.read()

            self.assertEqual(data, decrypted)


if __name__ == '__main__':
    unittest.main()
