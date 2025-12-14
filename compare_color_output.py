#!/usr/bin/env python3
"""对比生成的color音频和参考音频"""
import numpy as np
from scipy.io import wavfile

def compare_color(val):
    ref_file = f"tests/fixtures/a_color_tests/a_color_{val}.wav"
    gen_file = f"tests/output/test_a_color_{val}.wav"
    
    sr1, data1 = wavfile.read(ref_file)
    sr2, data2 = wavfile.read(gen_file)
    
    if data1.dtype == np.int16:
        data1 = data1.astype(np.float64) / 32768.0
        data2 = data2.astype(np.float64) / 32768.0
    
    if len(data1.shape) > 1:
        data1 = data1[:, 0]
        data2 = data2[:, 0]
    
    # 取中间段
    mid = len(data1) // 2
    seg1 = data1[mid:mid+sr1]
    seg2 = data2[mid:mid+sr2]
    
    # RMS
    rms1 = np.sqrt(np.mean(seg1**2))
    rms2 = np.sqrt(np.mean(seg2**2))
    
    # FFT
    fft1 = np.fft.rfft(seg1)
    fft2 = np.fft.rfft(seg2)
    freqs = np.fft.rfftfreq(len(seg1), 1/sr1)
    power1 = np.abs(fft1) ** 2
    power2 = np.abs(fft2) ** 2
    
    # 计算频谱斜率
    freq_range_mask = (freqs >= 200) & (freqs <= 10000)
    log_freqs = np.log10(freqs[freq_range_mask])
    log_power1 = np.log10(power1[freq_range_mask] + 1e-10)
    log_power2 = np.log10(power2[freq_range_mask] + 1e-10)
    
    slope1 = np.polyfit(log_freqs, log_power1, 1)[0]
    slope2 = np.polyfit(log_freqs, log_power2, 1)[0]
    
    # 频带能量
    bands = {
        'low': (0, 500),
        'mid': (500, 2000),
        'high': (5000, 15000)
    }
    
    def band_energy(power, freqs, band):
        mask = (freqs >= band[0]) & (freqs < band[1])
        return 100 * np.sum(power[mask]) / np.sum(power)
    
    print(f"\na_color={val}:")
    print(f"  RMS:    {rms1:.5f} vs {rms2:.5f}  (ratio: {rms2/rms1*100:.1f}%)")
    print(f"  Slope:  {slope1:.3f} vs {slope2:.3f}  (diff: {abs(slope1-slope2):.3f})")
    
    for band_name, band_range in bands.items():
        e1 = band_energy(power1, freqs, band_range)
        e2 = band_energy(power2, freqs, band_range)
        print(f"  {band_name:5s}: {e1:5.1f}% vs {e2:5.1f}%")

# 测试几个关键值
vals = ["0.0", "0.2518", "0.5506", "0.7489", "1.0"]
for val in vals:
    try:
        compare_color(val)
    except Exception as e:
        print(f"Error for {val}: {e}")
