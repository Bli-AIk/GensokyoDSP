#!/usr/bin/env python3
"""详细分析噪声的频谱特性"""
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

def analyze_detailed_spectrum(filepath, noise_val):
    """详细分析频谱"""
    sr, data = wavfile.read(filepath)
    
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 取稳定段
    mid_start = len(data) // 2
    mid_end = mid_start + sr
    segment = data[mid_start:mid_end]
    
    # FFT
    fft_data = np.fft.rfft(segment)
    freqs = np.fft.rfftfreq(len(segment), 1/sr)
    magnitude = np.abs(fft_data)
    power = magnitude ** 2
    
    # 基频 (C5 = 523.25 Hz)
    fund_freq = 523.25
    
    # 分析频带能量
    bands = {
        '0-200Hz': (0, 200),
        '200-400Hz': (200, 400),
        '400-600Hz': (400, 600),  # 包含基频
        '600-1000Hz': (600, 1000),
        '1k-2kHz': (1000, 2000),
        '2k-5kHz': (2000, 5000),
        '5k-10kHz': (5000, 10000),
        '10k-20kHz': (10000, 20000),
    }
    
    total_power = np.sum(power)
    
    print(f"\n=== a_noise = {noise_val} ===")
    print(f"总能量: {total_power:.2f}")
    print(f"\n频带能量分布:")
    
    for band_name, (f_low, f_high) in bands.items():
        mask = (freqs >= f_low) & (freqs < f_high)
        band_power = np.sum(power[mask])
        band_percent = 100 * band_power / total_power if total_power > 0 else 0
        print(f"  {band_name:12s}: {band_power:12.2f} ({band_percent:5.2f}%)")
    
    # 找到峰值频率
    peak_idx = np.argmax(magnitude)
    peak_freq = freqs[peak_idx]
    print(f"\n峰值频率: {peak_freq:.2f} Hz")
    print(f"基频能量: {magnitude[np.argmin(np.abs(freqs - fund_freq))]:.2f}")
    
    return freqs, magnitude

# 分析几个关键的噪声值
test_vals = ["0.4958", "0.5506", "0.7025", "0.9051", "1.0"]

plt.figure(figsize=(15, 10))

for idx, val in enumerate(test_vals):
    ref_file = f"tests/fixtures/a_noise_tests/a_noise_{val}.wav"
    gen_file = f"tests/output/test_a_noise_{val}.wav"
    
    print(f"\n{'='*70}")
    print(f"参考文件:")
    ref_freqs, ref_mag = analyze_detailed_spectrum(ref_file, val)
    
    print(f"\n生成文件:")
    gen_freqs, gen_mag = analyze_detailed_spectrum(gen_file, val)
    
    # 绘图
    plt.subplot(len(test_vals), 1, idx + 1)
    
    mask_ref = ref_freqs < 2000
    mask_gen = gen_freqs < 2000
    
    plt.plot(ref_freqs[mask_ref], 20*np.log10(ref_mag[mask_ref] + 1e-10), 
             'b-', label='参考', alpha=0.7, linewidth=2)
    plt.plot(gen_freqs[mask_gen], 20*np.log10(gen_mag[mask_gen] + 1e-10), 
             'r--', label='生成', alpha=0.7, linewidth=2)
    
    plt.axvline(523.25, color='green', linestyle=':', alpha=0.5, label='基频')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title(f'a_noise={val} (0-2kHz)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim([-60, 20])

plt.tight_layout()
plt.savefig('noise_spectrum_detail.png', dpi=150)
print("\n图表已保存到 noise_spectrum_detail.png")
