#!/usr/bin/env python3
"""Quick test to verify decryption works"""

from faro_cipher_ultra_optimized import UltraOptimizedFaroCipher
import os

def quick_test():
    # Create test data
    test_data = b'Hello, this is a test message for our cipher!'
    with open('test.txt', 'wb') as f:
        f.write(test_data)

    print("🧪 Quick decryption test")
    
    # Test encryption
    cipher = UltraOptimizedFaroCipher()
    print("🔐 Encrypting...")
    metadata = cipher.encrypt_file('test.txt', 'test.enc', progress=False)

    # Test decryption  
    print("🔓 Decrypting...")
    success = cipher.decrypt_file('test.enc', 'test.dec', metadata, progress=False)

    # Check result
    if success:
        with open('test.dec', 'rb') as f:
            decrypted = f.read()
        if decrypted == test_data:
            print('✅ SUCCESS: Decryption works correctly!')
            return True
        else:
            print('❌ FAILED: Data mismatch')
            print(f'Original:  {test_data}')
            print(f'Decrypted: {decrypted}')
            return False
    else:
        print('❌ FAILED: Decryption returned False')
        return False

if __name__ == "__main__":
    try:
        result = quick_test()
        
        # Cleanup
        for file in ['test.txt', 'test.enc', 'test.dec']:
            if os.path.exists(file):
                os.remove(file)
        
        if result:
            print("\n🎉 Quick test PASSED!")
        else:
            print("\n💥 Quick test FAILED!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 