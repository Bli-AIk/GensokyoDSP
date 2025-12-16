#!/usr/bin/env python3
"""深入分析b_freq测试的频率和振幅特征"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import signal, fft

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def analyze_spectrum(data, rate):
    """分析频谱"""
    # 使用中间稳定部分
    start_idx = int(0.5 * rate)
    end_idx = int(2.0 * rate)
    segment = data[start_idx:end_idx]
    
    # FFT
    fft_result = fft.rfft(segment)
    freqs = fft.rfftfreq(len(segment), 1/rate)
    magnitude = np.abs(fft_result)
    
    # 查找主频率
    peak_idx = np.argmax(magnitude)
    peak_freq = freqs[peak_idx]
    
    return freqs, magnitude, peak_freq

def analyze_b_freq(b_freq_value):
    """分析特定b_freq值"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        print(f"文件不存在: b_freq={b_freq_value}")
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 计算RMS
    ref_rms = np.sqrt(np.mean(ref_data**2))
    gen_rms = np.sqrt(np.mean(gen_data**2))
    
    # 计算峰值
    ref_peak = np.max(np.abs(ref_data))
    gen_peak = np.max(np.abs(gen_data))
    
    # 计算crest factor (peak/RMS)
    ref_crest = ref_peak / (ref_rms + 1e-10)
    gen_crest = gen_peak / (gen_rms + 1e-10)
    
    # 频谱分析
    ref_freqs, ref_mag, ref_peak_freq = analyze_spectrum(ref_data, ref_rate)
    gen_freqs, gen_mag, gen_peak_freq = analyze_spectrum(gen_data, gen_rate)
    
    results = {
        'b_freq': b_freq_value,
        'ref_rms': ref_rms,
        'gen_rms': gen_rms,
        'rms_ratio': gen_rms / (ref_rms + 1e-10),
        'ref_peak': ref_peak,
        'gen_peak': gen_peak,
        'peak_ratio': gen_peak / (ref_peak + 1e-10),
        'ref_crest': ref_crest,
        'gen_crest': gen_crest,
        'ref_peak_freq': ref_peak_freq,
        'gen_peak_freq': gen_peak_freq,
    }
    
    # 绘制频谱对比
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 2, 1)
    # 只显示前5000Hz
    max_freq_idx = np.where(ref_freqs <= 5000)[0][-1]
    plt.plot(ref_freqs[:max_freq_idx], 20*np.log10(ref_mag[:max_freq_idx] + 1e-10), 'b-', label='Reference', alpha=0.7)
    plt.plot(gen_freqs[:max_freq_idx], 20*np.log10(gen_mag[:max_freq_idx] + 1e-10), 'r-', label='Generated', alpha=0.7)
    plt.axvline(ref_peak_freq, color='b', linestyle='--', alpha=0.5, label=f'Ref peak: {ref_peak_freq:.1f} Hz')
    plt.axvline(gen_peak_freq, color='r', linestyle='--', alpha=0.5, label=f'Gen peak: {gen_peak_freq:.1f} Hz')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title(f'b_freq={b_freq_value} - Spectrum (0-5kHz)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    # 波形对比（前0.1秒）
    duration = 0.1
    ref_samples = int(duration * ref_rate)
    gen_samples = int(duration * gen_rate)
    time_ref = np.arange(ref_samples) / ref_rate
    time_gen = np.arange(gen_samples) / gen_rate
    plt.plot(time_ref, ref_data[:ref_samples], 'b-', label='Reference', alpha=0.7)
    plt.plot(time_gen, gen_data[:gen_samples], 'r-', label='Generated', alpha=0.7)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title(f'b_freq={b_freq_value} - Waveform')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'temps/b_freq_{b_freq_value}_analysis.png', dpi=150)
    plt.close()
    
    return results

def main():
    print("=" * 80)
    print("b_freq测试分析")
    print("=" * 80)
    
    Path('temps').mkdir(exist_ok=True)
    
    b_freq_values = [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051]
    
    all_results = []
    for b_freq_value in b_freq_values:
        print(f"\n分析 b_freq={b_freq_value}...")
        results = analyze_b_freq(b_freq_value)
        if results:
            all_results.append(results)
            print(f"  RMS: ref={results['ref_rms']:.6f}, gen={results['gen_rms']:.6f}, ratio={results['rms_ratio']:.4f}")
            print(f"  Peak: ref={results['ref_peak']:.6f}, gen={results['gen_peak']:.6f}, ratio={results['peak_ratio']:.4f}")
            print(f"  Crest: ref={results['ref_crest']:.4f}, gen={results['gen_crest']:.4f}")
            print(f"  Peak freq: ref={results['ref_peak_freq']:.1f} Hz, gen={results['gen_peak_freq']:.1f} Hz")
    
    if all_results:
        print("\n" + "=" * 80)
        print("振幅补偿需求:")
        print("=" * 80)
        print("b_freq  | RMS Ratio | Peak Ratio | Needed Gain")
        print("-" * 80)
        for r in all_results:
            needed_gain = 1.0 / r['rms_ratio']
            print(f"{r['b_freq']:.4f} | {r['rms_ratio']:9.4f} | {r['peak_ratio']:10.4f} | {needed_gain:11.4f}")
        
        # 查找模式
        print("\n" + "=" * 80)
        print("Crest Factor差异 (提示包络问题):")
        print("=" * 80)
        for r in all_results:
            crest_ratio = r['gen_crest'] / r['ref_crest']
            print(f"b_freq={r['b_freq']:.4f}: ref_crest={r['ref_crest']:.2f}, gen_crest={r['gen_crest']:.2f}, ratio={crest_ratio:.4f}")

if __name__ == "__main__":
    main()
