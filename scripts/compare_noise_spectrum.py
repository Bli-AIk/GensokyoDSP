#!/usr/bin/env python3
"""对比噪声的频谱特征"""
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

def analyze_spectrum(filepath):
    sr, data = wavfile.read(filepath)
    
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 取中间1秒
    mid_start = len(data) // 2
    mid_end = mid_start + sr
    segment = data[mid_start:mid_end]
    
    # FFT
    fft_data = np.fft.rfft(segment)
    freqs = np.fft.rfftfreq(len(segment), 1/sr)
    magnitude = np.abs(fft_data)
    
    return freqs, magnitude, np.sqrt(np.mean(segment**2))

# 对比不同噪声级别
vals = ["0.0547", "0.8080", "0.9515", "1.0"]
colors = ['blue', 'green', 'orange', 'red']

plt.figure(figsize=(15, 10))

for idx, (val, color) in enumerate(zip(vals, colors)):
    ref_file = f"tests/fixtures/a_noise_tests/a_noise_{val}.wav"
    gen_file = f"tests/output/test_a_noise_{val}.wav"
    
    plt.subplot(2, 2, idx + 1)
    
    try:
        ref_freqs, ref_mag, ref_rms = analyze_spectrum(ref_file)
        gen_freqs, gen_mag, gen_rms = analyze_spectrum(gen_file)
        
        # 绘制到10kHz
        mask_ref = ref_freqs < 10000
        mask_gen = gen_freqs < 10000
        
        plt.plot(ref_freqs[mask_ref], 20*np.log10(ref_mag[mask_ref] + 1e-10), 
                 'b-', label='参考', alpha=0.7, linewidth=2)
        plt.plot(gen_freqs[mask_gen], 20*np.log10(gen_mag[mask_gen] + 1e-10), 
                 'r--', label='生成', alpha=0.7, linewidth=2)
        
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.title(f'a_noise={val}\nRef RMS={ref_rms:.4f}, Gen RMS={gen_rms:.4f}')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim([-80, 0])
        
        # Calculate and print stats
        print(f"--- a_noise={val} ---")
        print(f"Ref RMS: {ref_rms:.6f}, Gen RMS: {gen_rms:.6f}, Diff: {gen_rms - ref_rms:.6f}")
        
        # Calculate average magnitude difference in dB
        min_len = min(len(ref_mag), len(gen_mag))
        ref_db = 20*np.log10(ref_mag[:min_len] + 1e-10)
        gen_db = 20*np.log10(gen_mag[:min_len] + 1e-10)
        avg_db_diff = np.mean(np.abs(ref_db - gen_db))
        print(f"Avg Spectrum Diff (dB): {avg_db_diff:.2f}")

    except Exception as e:
        print(f"Error processing {val}: {e}")

plt.tight_layout()
plt.savefig('noise_spectrum_comparison.png', dpi=150)
print("图表已保存到 noise_spectrum_comparison.png")
