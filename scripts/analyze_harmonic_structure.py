#!/usr/bin/env python3
"""
深入分析失败测试的谐波结构差异
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path

failing_tests = [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051]

def analyze_harmonics(b_freq_value):
    """分析谐波结构"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value:.4f}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value:.4f}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
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
    
    # 分析前10个谐波
    harmonics = []
    for n in range(1, 11):
        target_freq = fundamental * n
        # 找最接近的bin
        idx = np.argmin(np.abs(freqs - target_freq))
        if freqs[idx] < 20000:  # 在奈奎斯特频率内
            harmonics.append({
                'n': n,
                'freq': freqs[idx],
                'mag_ref': mag_ref[idx],
                'mag_gen': mag_gen[idx],
                'ratio': mag_gen[idx] / mag_ref[idx] if mag_ref[idx] > 100 else None
            })
    
    return {
        'b_freq': b_freq_value,
        'fundamental': fundamental,
        'harmonics': harmonics
    }

def main():
    print("=" * 100)
    print("失败测试的谐波分析")
    print("=" * 100)
    
    for b_freq in failing_tests:
        result = analyze_harmonics(b_freq)
        if not result:
            continue
        
        print(f"\nb_freq = {b_freq:.4f}, 基频 = {result['fundamental']:.2f}Hz")
        print("-" * 100)
        print(f"{'谐波#':<8} {'频率':<12} {'参考幅度':<15} {'生成幅度':<15} {'比率':<10} {'偏差':<10}")
        print("-" * 100)
        
        for h in result['harmonics']:
            if h['ratio'] is not None:
                deviation = (h['ratio'] - 1.0) * 100
                print(f"{h['n']:<8} {h['freq']:<12.2f} {h['mag_ref']:<15.2f} {h['mag_gen']:<15.2f} "
                      f"{h['ratio']:<10.4f} {deviation:>+9.1f}%")
            else:
                print(f"{h['n']:<8} {h['freq']:<12.2f} {h['mag_ref']:<15.2f} {h['mag_gen']:<15.2f} "
                      f"{'N/A':<10} {'N/A':>10}")
    
    # 总结模式
    print("\n" + "=" * 100)
    print("模式总结:")
    print("=" * 100)
    
    for b_freq in failing_tests:
        result = analyze_harmonics(b_freq)
        if not result:
            continue
        
        # 计算谐波比率的统计
        ratios = [h['ratio'] for h in result['harmonics'] 
                  if h['ratio'] is not None and h['mag_ref'] > 1000]
        
        if ratios:
            avg_ratio = np.mean(ratios)
            std_ratio = np.std(ratios)
            print(f"\nb_freq={b_freq:.4f}:")
            print(f"  有效谐波数: {len(ratios)}")
            print(f"  平均谐波比率: {avg_ratio:.4f}")
            print(f"  标准差: {std_ratio:.4f}")
            print(f"  谐波比率范围: {min(ratios):.4f} - {max(ratios):.4f}")
            
            # 检查是否有系统性问题
            if avg_ratio > 1.5:
                print(f"  问题: 谐波普遍过强 -> 需要整体降低{avg_ratio:.2f}x")
            elif avg_ratio < 0.7:
                print(f"  问题: 谐波普遍过弱 -> 需要整体提高{1/avg_ratio:.2f}x")
            elif std_ratio > 0.5:
                print(f"  问题: 谐波比率不稳定 -> 某些谐波失真")
            else:
                print(f"  问题: 相似度低但谐波比率接近1.0 -> 可能是相位问题")

if __name__ == "__main__":
    main()
