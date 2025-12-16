#!/usr/bin/env python3
"""分析各个谐波的相位关系"""

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

def analyze_harmonic_phases(b_freq_value):
    """分析各谐波的相位"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 使用稳定段
    start_idx = int(1.0 * ref_rate)
    end_idx = int(3.0 * ref_rate)
    ref_segment = ref_data[start_idx:end_idx]
    gen_segment = gen_data[start_idx:end_idx]
    
    # FFT（保留复数）
    ref_fft = fft.rfft(ref_segment)
    gen_fft = fft.rfft(gen_segment)
    ref_freqs = fft.rfftfreq(len(ref_segment), 1/ref_rate)
    
    # 找基频
    ref_mag = np.abs(ref_fft)
    peak_idx = np.argmax(ref_mag)
    fundamental = ref_freqs[peak_idx]
    
    print(f"\nb_freq={b_freq_value} (基频={fundamental:.1f} Hz):")
    print(f"  {'N':<3} | {'Ref Mag':<10} | {'Gen Mag':<10} | {'Mag Ratio':<10} | {'相位差(度)':<12} | {'状态':<10}")
    print(f"  {'-'*70}")
    
    phase_issues = []
    
    for n in range(1, 11):
        target_freq = fundamental * n
        tolerance = 20
        
        # 找谐波的bin
        mask = (ref_freqs >= target_freq - tolerance) & (ref_freqs <= target_freq + tolerance)
        if not np.any(mask):
            continue
        
        # 在范围内找峰值
        local_idx = np.where(mask)[0][np.argmax(ref_mag[mask])]
        
        # 获取复数值
        ref_complex = ref_fft[local_idx]
        gen_complex = gen_fft[local_idx]
        
        # 计算振幅和相位
        ref_amp = np.abs(ref_complex)
        gen_amp = np.abs(gen_complex)
        ref_phase = np.angle(ref_complex, deg=True)
        gen_phase = np.angle(gen_complex, deg=True)
        
        # 相位差
        phase_diff = gen_phase - ref_phase
        # 归一化到[-180, 180]
        while phase_diff > 180:
            phase_diff -= 360
        while phase_diff < -180:
            phase_diff += 360
        
        # 判断状态
        status = ""
        if abs(phase_diff) > 150:
            status = "反相!"
            phase_issues.append(n)
        elif abs(phase_diff) > 90:
            status = "偏移大"
        elif abs(phase_diff) > 45:
            status = "有偏移"
        else:
            status = "正常"
        
        mag_ratio = gen_amp / (ref_amp + 1e-10)
        
        print(f"  {n:<3} | {ref_amp:<10.1f} | {gen_amp:<10.1f} | {mag_ratio:<10.4f} | {phase_diff:<12.1f} | {status:<10}")
    
    if phase_issues:
        print(f"\n  警告: 谐波 {phase_issues} 有相位反转问题!")
    
    return {'b_freq': float(b_freq_value), 'phase_issues': phase_issues}

def main():
    Path('temps').mkdir(exist_ok=True)
    
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    results = []
    for b_freq_value in b_freq_values:
        result = analyze_harmonic_phases(b_freq_value)
        if result:
            results.append(result)
    
    print("\n" + "="*80)
    print("相位问题总结:")
    print("="*80)
    for r in results:
        if r['phase_issues']:
            print(f"b_freq={r['b_freq']:.4f}: 谐波 {r['phase_issues']} 有反相问题")
        else:
            print(f"b_freq={r['b_freq']:.4f}: 无相位问题")

if __name__ == "__main__":
    main()
