#!/usr/bin/env python3
"""
Test Ultra Optimization Performance (Phase 1)
Compare Numba JIT + Direct Binary vs Previous Version
"""

import os
import time
from pathlib import Path
import traceback

def create_test_file(size_kb: int, filename: str) -> str:
    """Create a test file of specified size in KB"""
    size_bytes = size_kb * 1024
    
    with open(filename, 'wb') as f:
        # Create realistic test data
        pattern = b"This is test data for ultra-optimized Faro cipher performance testing. " * 10
        
        remaining = size_bytes
        while remaining > 0:
            write_size = min(len(pattern), remaining)
            f.write(pattern[:write_size])
            remaining -= write_size
    
    return filename

def test_truly_optimized(test_file: str, size_kb: int) -> dict:
    """Test the previous truly optimized version"""
    
    try:
        from faro_cipher_truly_optimized import TrulyOptimizedFaroCipher
        
        print(f"🧪 Testing Truly Optimized (Previous Version):")
        print("-" * 50)
        
        # Initialize cipher
        cipher = TrulyOptimizedFaroCipher(chunk_size=4096)
        
        # Time the encryption
        output_file = test_file + ".truly_opt"
        
        start_time = time.time()
        metadata = cipher.encrypt_file(test_file, output_file, num_rounds=4, progress=False)
        end_time = time.time()
        
        elapsed = end_time - start_time
        throughput_mb_s = size_kb / (elapsed * 1024) if elapsed > 0 else 0
        
        # Check output
        output_size = Path(output_file).stat().st_size
        input_size = Path(test_file).stat().st_size
        expansion = output_size / input_size
        
        print(f"   Time: {elapsed:.3f} seconds")
        print(f"   Throughput: {throughput_mb_s:.3f} MB/s")
        print(f"   Output size: {output_size:,} bytes ({expansion:.2f}x expansion)")
        print(f"   Format: Base64 text")
        
        # Cleanup
        os.remove(output_file)
        if os.path.exists(output_file + ".meta.json"):
            os.remove(output_file + ".meta.json")
        
        return {
            'name': 'Truly Optimized',
            'time': elapsed,
            'throughput_mb_s': throughput_mb_s,
            'expansion': expansion,
            'success': True
        }
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        traceback.print_exc()
        return {
            'name': 'Truly Optimized',
            'time': float('inf'),
            'throughput_mb_s': 0,
            'expansion': 0,
            'success': False
        }

def test_ultra_optimized(test_file: str, size_kb: int) -> dict:
    """Test the new ultra optimized version"""
    
    try:
        from faro_cipher_ultra_optimized import UltraOptimizedFaroCipher
        
        print(f"🚀 Testing Ultra Optimized (Numba JIT + Direct Binary):")
        print("-" * 60)
        
        # Initialize cipher
        cipher = UltraOptimizedFaroCipher(chunk_size=4096)
        
        # Time the encryption
        output_file = test_file + ".ultra_opt"
        
        start_time = time.time()
        metadata = cipher.encrypt_file(test_file, output_file, num_rounds=4, progress=False)
        end_time = time.time()
        
        elapsed = end_time - start_time
        throughput_mb_s = size_kb / (elapsed * 1024) if elapsed > 0 else 0
        
        # Check output
        output_size = Path(output_file).stat().st_size
        input_size = Path(test_file).stat().st_size
        expansion = output_size / input_size
        
        print(f"   Time: {elapsed:.3f} seconds")
        print(f"   Throughput: {throughput_mb_s:.3f} MB/s")
        print(f"   Output size: {output_size:,} bytes ({expansion:.2f}x expansion)")
        print(f"   Format: Direct binary (no base64)")
        
        # Cleanup
        os.remove(output_file)
        if os.path.exists(output_file + ".meta.json"):
            os.remove(output_file + ".meta.json")
        
        return {
            'name': 'Ultra Optimized',
            'time': elapsed,
            'throughput_mb_s': throughput_mb_s,
            'expansion': expansion,
            'success': True
        }
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        traceback.print_exc()
        return {
            'name': 'Ultra Optimized',
            'time': float('inf'),
            'throughput_mb_s': 0,
            'expansion': 0,
            'success': False
        }

def run_ultra_optimization_test():
    """Run comprehensive test of Phase 1 optimizations"""
    
    print("🚀 Ultra Optimization Test (Phase 1)")
    print("=" * 50)
    print("Testing: Numba JIT Compilation + Direct Binary Output")
    print("Expected speedup: 3-5x over previous version")
    print("=" * 50)
    
    # Test different file sizes
    test_sizes = [1, 5, 10, 25, 50, 100]  # KB
    
    all_results = []
    
    for size_kb in test_sizes:
        print(f"\n📊 Testing {size_kb}KB file:")
        print("=" * 40)
        
        # Create test file
        test_file = f"ultra_test_{size_kb}kb.bin"
        create_test_file(size_kb, test_file)
        
        # Test truly optimized version
        truly_result = test_truly_optimized(test_file, size_kb)
        
        # Test ultra optimized version
        ultra_result = test_ultra_optimized(test_file, size_kb)
        
        # Calculate comparison
        if truly_result['success'] and ultra_result['success']:
            if truly_result['time'] > 0:
                speedup = truly_result['time'] / ultra_result['time']
                throughput_ratio = ultra_result['throughput_mb_s'] / truly_result['throughput_mb_s']
            else:
                speedup = float('inf')
                throughput_ratio = float('inf')
                
            print(f"\n📈 Phase 1 Optimization Results for {size_kb}KB:")
            print(f"   Time: {truly_result['time']:.3f}s → {ultra_result['time']:.3f}s")
            print(f"   Throughput: {truly_result['throughput_mb_s']:.3f} → {ultra_result['throughput_mb_s']:.3f} MB/s")
            print(f"   File size: {truly_result['expansion']:.2f}x → {ultra_result['expansion']:.2f}x expansion")
            
            if speedup >= 1:
                print(f"   🎯 Result: {speedup:.1f}x FASTER ✅")
            else:
                print(f"   ❌ Result: {1/speedup:.1f}x SLOWER")
            
            ultra_result['speedup'] = speedup
            ultra_result['throughput_ratio'] = throughput_ratio
        
        all_results.append({
            'size_kb': size_kb,
            'truly_optimized': truly_result,
            'ultra_optimized': ultra_result
        })
        
        # Cleanup
        os.remove(test_file)
    
    # Summary
    print("\n📊 PHASE 1 OPTIMIZATION SUMMARY")
    print("=" * 80)
    print(f"{'Size':<8} {'Truly Opt':<15} {'Ultra Opt':<15} {'Speedup':<12} {'Status'}")
    print("-" * 80)
    
    successful_results = []
    
    for result in all_results:
        size_kb = result['size_kb']
        truly = result['truly_optimized']
        ultra = result['ultra_optimized']
        
        if truly['success'] and ultra['success']:
            speedup = ultra.get('speedup', 0)
            if speedup >= 1:
                status = f"{speedup:.1f}x FASTER ✅"
            else:
                status = f"{1/speedup:.1f}x SLOWER ❌"
            
            print(f"{size_kb}KB{'':<4} {truly['throughput_mb_s']:.3f} MB/s{'':<3} {ultra['throughput_mb_s']:.3f} MB/s{'':<3} {speedup:.1f}x{'':<8} {status}")
            successful_results.append(result)
        else:
            print(f"{size_kb}KB{'':<4} {'Failed':<15} {'Failed':<15} {'N/A':<12} ❌")
    
    # Analysis
    if successful_results:
        print(f"\n📈 PHASE 1 RESULTS ANALYSIS")
        print("=" * 40)
        
        # Calculate averages
        truly_avg = sum(r['truly_optimized']['throughput_mb_s'] for r in successful_results) / len(successful_results)
        ultra_avg = sum(r['ultra_optimized']['throughput_mb_s'] for r in successful_results) / len(successful_results)
        avg_speedup = sum(r['ultra_optimized'].get('speedup', 0) for r in successful_results) / len(successful_results)
        
        print(f"Average Truly Optimized: {truly_avg:.3f} MB/s")
        print(f"Average Ultra Optimized: {ultra_avg:.3f} MB/s")
        print(f"Average Phase 1 Speedup: {avg_speedup:.1f}x")
        
        # Best and worst performance
        best_speedup = max(r['ultra_optimized'].get('speedup', 0) for r in successful_results)
        worst_speedup = min(r['ultra_optimized'].get('speedup', 0) for r in successful_results)
        
        print(f"Best Phase 1 Speedup: {best_speedup:.1f}x")
        print(f"Worst Phase 1 Speedup: {worst_speedup:.1f}x")
        
        # File size analysis
        print(f"\nFile Size Analysis:")
        truly_avg_expansion = sum(r['truly_optimized']['expansion'] for r in successful_results) / len(successful_results)
        ultra_avg_expansion = sum(r['ultra_optimized']['expansion'] for r in successful_results) / len(successful_results)
        
        print(f"Truly Opt avg expansion: {truly_avg_expansion:.2f}x (base64)")
        print(f"Ultra Opt avg expansion: {ultra_avg_expansion:.2f}x (binary)")
        
        size_reduction = (truly_avg_expansion - ultra_avg_expansion) / truly_avg_expansion * 100
        print(f"File size reduction: {size_reduction:.1f}% smaller files!")
        
        print(f"\n🎉 PHASE 1 VERDICT")
        print("=" * 30)
        if avg_speedup >= 3:
            print(f"✅ PHASE 1 EXCEEDED EXPECTATIONS!")
            print(f"✅ Achieved {avg_speedup:.1f}x speedup (target was 3-5x)")
        elif avg_speedup >= 1.5:
            print(f"✅ PHASE 1 SUCCESSFUL!")
            print(f"✅ Achieved {avg_speedup:.1f}x speedup")
        else:
            print(f"❌ PHASE 1 UNDERPERFORMED")
            print(f"❌ Only achieved {avg_speedup:.1f}x speedup")
        
        print(f"✅ Additional benefits:")
        print(f"   • {size_reduction:.1f}% smaller output files")
        print(f"   • Binary format (faster I/O)")
        print(f"   • JIT compilation warmup for future runs")
        
        # Project improvements to 0.5 GB
        print(f"\n🔮 Impact on 0.5 GB file:")
        print(f"   Truly Optimized: ~{500/truly_avg:.0f} minutes")
        print(f"   Ultra Optimized: ~{500/ultra_avg:.0f} minutes")
        print(f"   Improvement: {avg_speedup:.1f}x faster processing!")
    
    else:
        print("❌ Unable to complete Phase 1 analysis - tests failed")

if __name__ == "__main__":
    print("🧪 Testing Phase 1 Ultra Optimizations")
    print("Numba JIT Compilation + Direct Binary Output")
    print("=" * 60)
    
    try:
        run_ultra_optimization_test()
        
        print("\n🏁 Phase 1 testing completed!")
        print("Next steps: Phase 2 (Multi-threading + Streaming I/O)")
        
    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        traceback.print_exc() 