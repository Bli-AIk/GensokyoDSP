#!/usr/bin/env python3
"""详细分析波形相关性问题"""

import numpy as np
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import signal

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def analyze_waveform_correlation(b_freq_value):
    """分析波形相关性"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 分析不同时间段的相关性
    segments = [
        ('起音', 0.0, 0.5),
        ('稳定', 1.0, 3.0),
        ('全程', 0.0, 5.0),
    ]
    
    print(f"\nb_freq={b_freq_value}:")
    print(f"  {'时段':<10} | {'相关系数':<12} | {'RMS比':<12} | {'峰值比':<12}")
    print(f"  {'-'*50}")
    
    for seg_name, start_t, end_t in segments:
        start_idx = int(start_t * ref_rate)
        end_idx = int(end_t * ref_rate)
        
        ref_seg = ref_data[start_idx:end_idx]
        gen_seg = gen_data[start_idx:end_idx]
        
        # 计算相关系数
        min_len = min(len(ref_seg), len(gen_seg))
        ref_seg = ref_seg[:min_len]
        gen_seg = gen_seg[:min_len]
        
        # 归一化相关系数
        rms_ref = np.sqrt(np.mean(ref_seg**2))
        rms_gen = np.sqrt(np.mean(gen_seg**2))
        
        if rms_ref > 0 and rms_gen > 0:
            corr = np.mean(ref_seg * gen_seg) / (rms_ref * rms_gen)
            rms_ratio = rms_gen / rms_ref
            peak_ratio = np.max(np.abs(gen_seg)) / np.max(np.abs(ref_seg))
        else:
            corr = 0.0
            rms_ratio = 0.0
            peak_ratio = 0.0
        
        similarity = (corr + 1.0) / 2.0 * 100.0
        
        print(f"  {seg_name:<10} | {corr:>6.4f} ({similarity:>5.1f}%) | {rms_ratio:>6.4f} ({rms_ratio*100:>5.1f}%) | {peak_ratio:>6.4f} ({peak_ratio*100:>5.1f}%)")
    
    # 分析相位对齐问题
    # 使用稳定段
    start_idx = int(1.0 * ref_rate)
    end_idx = int(2.0 * ref_rate)
    ref_seg = ref_data[start_idx:end_idx]
    gen_seg = gen_data[start_idx:end_idx]
    
    # 计算交叉相关找相位偏移
    correlation = signal.correlate(ref_seg, gen_seg[:len(ref_seg)], mode='same')
    lags = signal.correlation_lags(len(ref_seg), len(gen_seg[:len(ref_seg)]), mode='same')
    lag = lags[np.argmax(correlation)]
    
    print(f"  最佳相位偏移: {lag} 采样点 ({lag / ref_rate * 1000:.2f} ms)")
    
    return {
        'b_freq': float(b_freq_value),
        'correlation': corr,
        'similarity': similarity,
        'rms_ratio': rms_ratio,
        'lag': lag
    }

def main():
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    results = []
    for b_freq_value in b_freq_values:
        result = analyze_waveform_correlation(b_freq_value)
        if result:
            results.append(result)
    
    if results:
        print("\n" + "="*80)
        print("总结:")
        print("="*80)
        print(f"{'b_freq':<10} | {'相关系数':<12} | {'相似度':<12} | {'RMS比':<12}")
        print("-"*80)
        for r in results:
            print(f"{r['b_freq']:<10.4f} | {r['correlation']:<12.4f} | {r['similarity']:<12.2f} | {r['rms_ratio']:<12.4f}")

if __name__ == "__main__":
    main()
