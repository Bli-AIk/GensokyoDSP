#!/usr/bin/env python3
"""
详细分析b_freq失败测试，找出RMS补偿的精确调整方案
"""

import numpy as np
import wave
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(str(filename), 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        frames = wav.readframes(n_frames)
        
        if sample_width == 2:
            data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:
            data = np.frombuffer(frames, dtype=np.int32)
        else:
            raise ValueError(f"不支持的采样位深: {sample_width}")
        
        data = data.astype(np.float64) / (2**(sample_width * 8 - 1))
        
        if n_channels == 2:
            data = data[::2]
        
        return data, framerate

def analyze_b_freq_test(b_freq_value):
    """分析单个b_freq测试"""
    base_path = Path("/workspaces/GensokyoDSP")
    
    ref_file = base_path / "tests" / "fixtures" / "b_freq_tests" / f"b_freq_{b_freq_value}.wav"
    test_file = base_path / "tests" / "output" / f"test_b_freq_{b_freq_value}.wav"
    
    if not ref_file.exists() or not test_file.exists():
        return None
    
    ref_data, ref_sr = read_wav(ref_file)
    test_data, test_sr = read_wav(test_file)
    
    # 计算RMS
    ref_rms = np.sqrt(np.mean(ref_data**2))
    test_rms = np.sqrt(np.mean(test_data**2))
    
    # 计算稳态RMS（后半段）
    half = len(ref_data) // 2
    ref_steady = np.sqrt(np.mean(ref_data[half:]**2))
    test_steady = np.sqrt(np.mean(test_data[half:]**2))
    
    # 计算峰值
    ref_peak = np.max(np.abs(ref_data))
    test_peak = np.max(np.abs(test_data))
    
    return {
        'value': b_freq_value,
        'ref_rms': ref_rms,
        'test_rms': test_rms,
        'rms_ratio': test_rms / ref_rms,
        'ref_steady': ref_steady,
        'test_steady': test_steady,
        'steady_ratio': test_steady / ref_steady,
        'ref_peak': ref_peak,
        'test_peak': test_peak,
        'peak_ratio': test_peak / ref_peak,
    }

def main():
    # b_freq值和对应的实际频率
    # a_freq = 0.5 -> 523.25 Hz (基频)
    freq_a = 523.25
    
    test_cases = [
        ('0.4958', freq_a * 0.12497),   # 64.2 Hz
        ('0.5506', freq_a * 0.24939),   # 130.5 Hz
        ('0.6519', freq_a * 0.48381),   # 253.1 Hz
        ('0.8080', freq_a * 4.0),       # 2093 Hz
        ('0.8502', freq_a * 7.17497),   # 3754 Hz
        ('0.9051', freq_a * 10.64416),  # 5569 Hz
    ]
    
    print("b_freq详细分析:")
    print("=" * 100)
    print(f"{'b_freq':<10} {'频率B(Hz)':<12} {'参考RMS':<12} {'测试RMS':<12} {'RMS比':<10} {'需要调整':<12}")
    print("-" * 100)
    
    results = []
    for value, freq_b in test_cases:
        result = analyze_b_freq_test(value)
        if result:
            results.append((result, freq_b))
            needed_gain = result['ref_rms'] / result['test_rms']
            
            print(f"{value:<10} {freq_b:<12.2f} {result['ref_rms']:<12.6f} "
                  f"{result['test_rms']:<12.6f} {result['rms_ratio']:<10.3f} {needed_gain:<12.4f}")
    
    print("\n" + "=" * 100)
    print("稳态RMS分析（后半段）:")
    print("=" * 100)
    print(f"{'b_freq':<10} {'频率B(Hz)':<12} {'参考稳态':<12} {'测试稳态':<12} {'稳态比':<10} {'需要调整':<12}")
    print("-" * 100)
    
    for (result, freq_b) in results:
        needed_gain = result['ref_steady'] / result['test_steady']
        
        print(f"{result['value']:<10} {freq_b:<12.2f} {result['ref_steady']:<12.6f} "
              f"{result['test_steady']:<12.6f} {result['steady_ratio']:<10.3f} {needed_gain:<12.4f}")
    
    # 分析趋势
    print("\n" + "=" * 100)
    print("当前补偿 vs 需要的补偿:")
    print("=" * 100)
    
    print(f"{'频率B(Hz)':<12} {'当前补偿':<12} {'实际稳态比':<15} {'需要补偿':<12} {'差异':<12}")
    print("-" * 100)
    
    for (result, freq_b) in results:
        # 估算当前补偿（从synthesizer.rs第255-275行）
        if freq_b < 150:
            current = 0.87 + (freq_b - 65.0) / (150.0 - 65.0) * (0.96 - 0.87)
        elif freq_b < 500:
            current = 0.96 + (freq_b - 150.0) / (500.0 - 150.0) * (1.0 - 0.96)
        elif freq_b < 1500:
            current = 1.0
        elif freq_b < 3000:
            current = 1.0 + (freq_b - 1500.0) / (3000.0 - 1500.0) * (1.3 - 1.0)
        elif freq_b < 5000:
            current = 1.3 + (freq_b - 3000.0) / (5000.0 - 3000.0) * (1.6 - 1.3)
        else:
            base = 1.6
            extra = ((freq_b - 5000.0) / 1000.0) * 0.1
            current = min(base + extra, 1.8)
        
        needed = 1.0 / result['steady_ratio']
        diff = needed - current
        
        print(f"{freq_b:<12.2f} {current:<12.3f} {result['steady_ratio']:<15.3f} "
              f"{needed:<12.4f} {diff:+12.4f}")

if __name__ == "__main__":
    main()
