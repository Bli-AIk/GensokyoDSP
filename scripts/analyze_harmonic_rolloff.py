#!/usr/bin/env python3
"""分析高频衰减的原因"""

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

def analyze_rolloff(b_freq_value):
    """分析高频衰减"""
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
    fundamental = ref_freqs[ref_peak_idx]
    
    # 绘制谱图
    plt.figure(figsize=(15, 10))
    
    # 全频谱
    plt.subplot(2, 2, 1)
    max_freq = 10000
    mask_r = ref_freqs <= max_freq
    mask_g = gen_freqs <= max_freq
    plt.plot(ref_freqs[mask_r], 20*np.log10(ref_mag[mask_r] + 1e-10), 'b-', label='Reference', alpha=0.7)
    plt.plot(gen_freqs[mask_g], 20*np.log10(gen_mag[mask_g] + 1e-10), 'r-', label='Generated', alpha=0.7)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title(f'b_freq={b_freq_value} - Full Spectrum')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 谐波衰减率
    plt.subplot(2, 2, 2)
    harmonics_n = np.arange(1, 11)
    ref_harmonics = []
    gen_harmonics = []
    
    for n in harmonics_n:
        target_freq = fundamental * n
        tolerance = 20
        
        # Reference
        mask_r = (ref_freqs >= target_freq - tolerance) & (ref_freqs <= target_freq + tolerance)
        if np.any(mask_r):
            ref_harmonics.append(np.max(ref_mag[mask_r]))
        else:
            ref_harmonics.append(0)
        
        # Generated
        mask_g = (gen_freqs >= target_freq - tolerance) & (gen_freqs <= target_freq + tolerance)
        if np.any(mask_g):
            gen_harmonics.append(np.max(gen_mag[mask_g]))
        else:
            gen_harmonics.append(0)
    
    ref_harmonics = np.array(ref_harmonics)
    gen_harmonics = np.array(gen_harmonics)
    
    plt.plot(harmonics_n, 20*np.log10(ref_harmonics + 1e-10), 'b-o', label='Reference', linewidth=2)
    plt.plot(harmonics_n, 20*np.log10(gen_harmonics + 1e-10), 'r-o', label='Generated', linewidth=2)
    plt.xlabel('Harmonic Number')
    plt.ylabel('Magnitude (dB)')
    plt.title(f'Harmonic Rolloff (Fund={fundamental:.1f} Hz)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 谐波比率
    plt.subplot(2, 2, 3)
    ratios = gen_harmonics / (ref_harmonics + 1e-10)
    plt.plot(harmonics_n, ratios, 'g-o', linewidth=2)
    plt.axhline(1.0, color='k', linestyle='--', alpha=0.5)
    plt.xlabel('Harmonic Number')
    plt.ylabel('Gen/Ref Ratio')
    plt.title('Harmonic Amplitude Ratio')
    plt.grid(True, alpha=0.3)
    
    # 差异频谱
    plt.subplot(2, 2, 4)
    # 对齐频率bins
    min_len = min(len(ref_mag), len(gen_mag))
    diff = gen_mag[:min_len] - ref_mag[:min_len]
    diff_db = 20*np.log10(np.abs(diff) + 1e-10)
    
    mask = ref_freqs[:min_len] <= max_freq
    plt.plot(ref_freqs[:min_len][mask], diff_db[mask], 'purple', alpha=0.7)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Difference (dB)')
    plt.title('Spectral Difference')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'temps/b_freq_{b_freq_value}_rolloff.png', dpi=150)
    plt.close()
    
    print(f"\nb_freq={b_freq_value} (fundamental={fundamental:.1f} Hz):")
    print(f"  {'N':<3} | {'Ref (dB)':<10} | {'Gen (dB)':<10} | {'Ratio':<8} | {'dB Diff':<8}")
    print(f"  {'-'*50}")
    for i, n in enumerate(harmonics_n):
        ref_db = 20*np.log10(ref_harmonics[i] + 1e-10)
        gen_db = 20*np.log10(gen_harmonics[i] + 1e-10)
        ratio = ratios[i]
        db_diff = gen_db - ref_db
        print(f"  {n:<3} | {ref_db:<10.1f} | {gen_db:<10.1f} | {ratio:<8.4f} | {db_diff:<8.1f}")
    
    avg_ratio_h2_plus = np.mean(ratios[1:])
    print(f"\n  平均谐波比率 (h2-h10): {avg_ratio_h2_plus:.4f}")
    print(f"  需要的谐波增益: {1/avg_ratio_h2_plus:.4f}x")

def main():
    Path('temps').mkdir(exist_ok=True)
    
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    for b_freq_value in b_freq_values:
        analyze_rolloff(b_freq_value)

if __name__ == "__main__":
    main()
