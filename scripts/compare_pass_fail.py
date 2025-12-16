#!/usr/bin/env python3
"""
对比通过和失败的b_freq测试
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path
import matplotlib.pyplot as plt

def analyze_test(b_freq_value, label):
    """分析单个测试"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value:.4f}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value:.4f}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        print(f"文件不存在: {b_freq_value}")
        return None
    
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
    
    # 计算FFT
    fft_ref = np.fft.rfft(audio_ref)
    fft_gen = np.fft.rfft(audio_gen)
    freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)
    
    mag_ref = np.abs(fft_ref)
    mag_gen = np.abs(fft_gen)
    
    # 找基频
    peak_idx = np.argmax(mag_ref[10:]) + 10
    fundamental = freqs[peak_idx]
    
    print(f"\n{'='*80}")
    print(f"{label}: b_freq={b_freq_value:.4f}, 基频={fundamental:.2f}Hz")
    print(f"{'='*80}")
    
    # 分析前15个谐波
    print(f"\n{'谐波#':<6} {'频率(Hz)':<12} {'参考幅度':<15} {'生成幅度':<15} {'比率':<10}")
    print("-" * 70)
    
    harmonic_ratios = []
    for n in range(1, 16):
        target_freq = fundamental * n
        idx = np.argmin(np.abs(freqs - target_freq))
        if freqs[idx] < 20000 and mag_ref[idx] > 50:  # 在奈奎斯特频率内且有意义
            ratio = mag_gen[idx] / mag_ref[idx] if mag_ref[idx] > 0 else 0
            harmonic_ratios.append((n, ratio))
            print(f"{n:<6} {freqs[idx]:<12.2f} {mag_ref[idx]:<15.2f} {mag_gen[idx]:<15.2f} {ratio:<10.4f}")
    
    # 计算谐波衰减曲线
    if len(harmonic_ratios) >= 5:
        # 参考音频的谐波衰减
        ref_harmonics = [(n, mag_ref[np.argmin(np.abs(freqs - fundamental * n))]) 
                         for n in range(1, 11) 
                         if fundamental * n < 20000]
        gen_harmonics = [(n, mag_gen[np.argmin(np.abs(freqs - fundamental * n))]) 
                         for n in range(1, 11) 
                         if fundamental * n < 20000]
        
        # 归一化到第一谐波
        if len(ref_harmonics) > 0 and ref_harmonics[0][1] > 0:
            ref_norm = [(n, mag / ref_harmonics[0][1]) for n, mag in ref_harmonics]
            gen_norm = [(n, mag / ref_harmonics[0][1]) for n, mag in gen_harmonics]
            
            print(f"\n归一化谐波强度（相对于基频）:")
            print(f"{'谐波#':<6} {'参考':<12} {'生成':<12} {'差异':<12}")
            print("-" * 50)
            for i, ((n_ref, mag_ref_norm), (n_gen, mag_gen_norm)) in enumerate(zip(ref_norm, gen_norm)):
                diff = mag_gen_norm - mag_ref_norm
                print(f"{n_ref:<6} {mag_ref_norm:<12.6f} {mag_gen_norm:<12.6f} {diff:>+12.6f}")
    
    return {
        'b_freq': b_freq_value,
        'fundamental': fundamental,
        'harmonic_ratios': harmonic_ratios
    }

def main():
    # 对比一个通过的和一个失败的
    passing = 0.7489  # 通过的测试
    failing = 0.4958  # 失败的测试
    
    result_pass = analyze_test(passing, "PASS")
    result_fail = analyze_test(failing, "FAIL")
    
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    
    if result_pass and result_fail:
        print(f"\n通过测试 (b_freq={passing}):")
        if len(result_pass['harmonic_ratios']) > 0:
            ratios = [r for _, r in result_pass['harmonic_ratios']]
            print(f"  谐波比率范围: {min(ratios):.4f} - {max(ratios):.4f}")
            print(f"  平均比率: {np.mean(ratios):.4f}")
        
        print(f"\n失败测试 (b_freq={failing}):")
        if len(result_fail['harmonic_ratios']) > 0:
            ratios = [r for _, r in result_fail['harmonic_ratios']]
            print(f"  谐波比率范围: {min(ratios):.4f} - {max(ratios):.4f}")
            print(f"  平均比率: {np.mean(ratios):.4f}")
            
            # 找出问题谐波
            print(f"\n  问题谐波（比率 > 2.0 或 < 0.5）:")
            for n, r in result_fail['harmonic_ratios']:
                if r > 2.0 or r < 0.5:
                    print(f"    谐波#{n}: {r:.4f}")

if __name__ == "__main__":
    main()
