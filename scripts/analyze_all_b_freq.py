#!/usr/bin/env python3
"""
分析所有 b_freq 测试，找出通过和失败的模式
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path
import re

# b_freq值到量化比率的映射（从synthesizer.rs复制）
def quantize_b_freq_ratio(p):
    if p < 0.48:
        return 1.0
    elif p < 0.52:
        return 0.12497  # 1/8
    elif p < 0.57:
        return 0.24939  # 130Hz when A=523Hz
    elif p < 0.62:
        return 0.48381  # 253Hz
    elif p < 0.67:
        return 0.58891  # 308Hz
    elif p < 0.69:
        return 1.0      # 523Hz (Unison)
    elif p < 0.72:
        return 1.00901  # 528Hz
    elif p < 0.77:
        return 2.0      # 1046Hz
    elif p < 0.82:
        return 4.0      # 2093Hz
    elif p < 0.87:
        return 7.17497  # 3754Hz
    elif p < 0.92:
        return 10.64416 # 5569Hz
    elif p < 0.97:
        return 16.09951 # 8424Hz
    else:
        return 32.0     # 16744Hz

def analyze_b_freq_test(b_freq_value):
    """分析单个b_freq测试"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value:.4f}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value:.4f}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    try:
        sr_ref, audio_ref = wavfile.read(ref_file)
        sr_gen, audio_gen = wavfile.read(gen_file)
        
        # 转换为浮点数
        if audio_ref.dtype == np.int16:
            audio_ref = audio_ref.astype(np.float32) / 32768.0
        if audio_gen.dtype == np.int16:
            audio_gen = audio_gen.astype(np.float32) / 32768.0
        
        # 只取单声道
        if len(audio_ref.shape) > 1:
            audio_ref = audio_ref[:, 0]
        if len(audio_gen.shape) > 1:
            audio_gen = audio_gen[:, 0]
        
        # 确保长度一致
        min_len = min(len(audio_ref), len(audio_gen))
        audio_ref = audio_ref[:min_len]
        audio_gen = audio_gen[:min_len]
        
        # 计算 RMS
        rms_ref = np.sqrt(np.mean(audio_ref**2))
        rms_gen = np.sqrt(np.mean(audio_gen**2))
        
        # 计算FFT找主频
        fft_ref = np.fft.rfft(audio_ref)
        freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)
        mag_ref = np.abs(fft_ref)
        
        # 找最强的频率（跳过DC）
        peak_idx = np.argmax(mag_ref[10:]) + 10
        dominant_freq = freqs[peak_idx]
        
        # 计算理论频率
        freq_a = 523.0  # a_freq=0.5对应523Hz
        b_ratio = quantize_b_freq_ratio(b_freq_value)
        expected_freq = freq_a * b_ratio
        
        return {
            'b_freq': b_freq_value,
            'b_ratio': b_ratio,
            'expected_freq': expected_freq,
            'dominant_freq': dominant_freq,
            'rms_ref': rms_ref,
            'rms_gen': rms_gen,
            'rms_ratio': rms_gen / rms_ref if rms_ref > 0 else 0,
        }
    except Exception as e:
        print(f"Error analyzing {b_freq_value}: {e}")
        return None

def main():
    # 所有测试值
    all_tests = [
        0.0547, 0.1058, 0.1496, 0.2007, 0.2518,
        0.3102, 0.3540, 0.4051, 0.4536, 0.4958,
        0.5506, 0.6055, 0.6519, 0.7025, 0.7489,
        0.8080, 0.8502, 0.9051, 0.9515, 1.0
    ]
    
    # 失败的测试（从cargo test输出）
    failing = {0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051}
    
    print("=" * 100)
    print(f"{'b_freq':<8} {'状态':<6} {'B比率':<10} {'预期频率':<12} {'实际频率':<12} {'RMS参考':<10} {'RMS生成':<10} {'RMS比率':<10}")
    print("=" * 100)
    
    results = []
    for b_freq in all_tests:
        result = analyze_b_freq_test(b_freq)
        if result:
            status = "FAIL" if b_freq in failing else "PASS"
            print(f"{result['b_freq']:<8.4f} {status:<6} {result['b_ratio']:<10.5f} "
                  f"{result['expected_freq']:<12.2f} {result['dominant_freq']:<12.2f} "
                  f"{result['rms_ref']:<10.6f} {result['rms_gen']:<10.6f} "
                  f"{result['rms_ratio']:<10.4f}")
            results.append((result, status))
    
    print("\n" + "=" * 100)
    print("失败测试的分组分析:")
    print("=" * 100)
    
    # 按频率范围分组
    freq_ranges = [
        (0, 100, "< 100Hz"),
        (100, 300, "100-300Hz"),
        (300, 600, "300-600Hz"),
        (600, 1000, "600-1000Hz"),
        (1000, 2000, "1000-2000Hz"),
        (2000, 4000, "2000-4000Hz"),
        (4000, 6000, "4000-6000Hz"),
        (6000, float('inf'), "> 6000Hz"),
    ]
    
    for min_f, max_f, label in freq_ranges:
        in_range = [(r, s) for r, s in results 
                    if min_f <= r['expected_freq'] < max_f]
        if not in_range:
            continue
        
        passing = [r for r, s in in_range if s == "PASS"]
        failing_r = [r for r, s in in_range if s == "FAIL"]
        
        print(f"\n{label}:")
        print(f"  通过: {len(passing)}, 失败: {len(failing_r)}")
        
        if failing_r:
            print(f"  失败测试的RMS比率: {[f'{r['rms_ratio']:.4f}' for r in failing_r]}")
            avg_ratio = np.mean([r['rms_ratio'] for r in failing_r])
            print(f"  平均RMS比率: {avg_ratio:.4f}")
            print(f"  需要的补偿调整: {1/avg_ratio:.4f}x")

if __name__ == "__main__":
    main()
