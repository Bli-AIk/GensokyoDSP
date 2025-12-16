#!/usr/bin/env python3
"""详细分析b_freq测试的谐波结构"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import fft

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def find_harmonics(freqs, magnitude, fundamental, num_harmonics=10):
    """找到谐波峰值"""
    harmonics = []
    
    for n in range(1, num_harmonics + 1):
        target_freq = fundamental * n
        # 在±20Hz范围内查找峰值
        tolerance = 20
        mask = (freqs >= target_freq - tolerance) & (freqs <= target_freq + tolerance)
        
        if np.any(mask):
            local_freqs = freqs[mask]
            local_mag = magnitude[mask]
            peak_idx = np.argmax(local_mag)
            harmonics.append({
                'n': n,
                'freq': local_freqs[peak_idx],
                'magnitude': local_mag[peak_idx]
            })
    
    return harmonics

def analyze_b_freq_harmonics(b_freq_value):
    """分析b_freq的谐波结构"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 使用稳定段进行FFT
    start_idx = int(1.0 * ref_rate)
    end_idx = int(3.0 * ref_rate)
    ref_segment = ref_data[start_idx:end_idx]
    gen_segment = gen_data[start_idx:end_idx]
    
    # FFT
    ref_fft = fft.rfft(ref_segment)
    gen_fft = fft.rfft(gen_segment)
    ref_freqs = fft.rfftfreq(len(ref_segment), 1/ref_rate)
    gen_freqs = fft.rfftfreq(len(gen_segment), 1/gen_rate)
    ref_mag = np.abs(ref_fft)
    gen_mag = np.abs(gen_fft)
    
    # 找基频
    ref_peak_idx = np.argmax(ref_mag)
    gen_peak_idx = np.argmax(gen_mag)
    ref_fundamental = ref_freqs[ref_peak_idx]
    gen_fundamental = gen_freqs[gen_peak_idx]
    
    # 找谐波
    ref_harmonics = find_harmonics(ref_freqs, ref_mag, ref_fundamental)
    gen_harmonics = find_harmonics(gen_freqs, gen_mag, gen_fundamental)
    
    print(f"\nb_freq={b_freq_value}:")
    print(f"  基频: ref={ref_fundamental:.1f} Hz, gen={gen_fundamental:.1f} Hz")
    print(f"\n  谐波对比:")
    print(f"  {'N':<3} | {'Ref Freq':<10} | {'Ref Mag':<10} | {'Gen Freq':<10} | {'Gen Mag':<10} | {'Mag Ratio':<10}")
    print(f"  {'-'*70}")
    
    for i in range(min(len(ref_harmonics), len(gen_harmonics))):
        ref_h = ref_harmonics[i]
        gen_h = gen_harmonics[i]
        ratio = gen_h['magnitude'] / (ref_h['magnitude'] + 1e-10)
        print(f"  {ref_h['n']:<3} | {ref_h['freq']:<10.1f} | {ref_h['magnitude']:<10.2f} | {gen_h['freq']:<10.1f} | {gen_h['magnitude']:<10.2f} | {ratio:<10.4f}")
    
    # 计算总谐波能量比率
    ref_total = sum(h['magnitude'] for h in ref_harmonics)
    gen_total = sum(h['magnitude'] for h in gen_harmonics)
    total_ratio = gen_total / (ref_total + 1e-10)
    print(f"\n  总谐波能量比率: {total_ratio:.4f}")
    print(f"  需要的增益: {1/total_ratio:.4f}")
    
    return {
        'b_freq': b_freq_value,
        'fundamental_ratio': gen_fundamental / ref_fundamental,
        'harmonic_ratio': total_ratio,
        'needed_gain': 1 / total_ratio
    }

def main():
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    results = []
    for b_freq_value in b_freq_values:
        result = analyze_b_freq_harmonics(b_freq_value)
        if result:
            results.append(result)
    
    if results:
        print("\n" + "="*80)
        print("总结:")
        print("="*80)
        print(f"{'b_freq':<10} | {'Harmonic Ratio':<15} | {'Needed Gain':<15}")
        print("-"*80)
        for r in results:
            print(f"{r['b_freq']:<10} | {r['harmonic_ratio']:<15.4f} | {r['needed_gain']:<15.4f}")

if __name__ == "__main__":
    main()
