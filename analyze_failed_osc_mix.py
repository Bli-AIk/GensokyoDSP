import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

def analyze_pair(ref_file, test_file, title):
    rate_ref, data_ref = wavfile.read(ref_file)
    rate_test, data_test = wavfile.read(test_file)
    
    if len(data_ref.shape) > 1:
        data_ref = data_ref[:, 0]
    if len(data_test.shape) > 1:
        data_test = data_test[:, 0]
    
    data_ref = data_ref.astype(np.float32) / 32768.0
    data_test = data_test.astype(np.float32) / 32768.0
    
    # FFT
    window_size = min(rate_ref, len(data_ref))
    window = np.hanning(window_size)
    
    fft_ref = np.fft.rfft(data_ref[:window_size] * window)
    fft_test = np.fft.rfft(data_test[:window_size] * window)
    
    freqs = np.fft.rfftfreq(window_size, 1/rate_ref)
    mag_ref = np.abs(fft_ref)
    mag_test = np.abs(fft_test)
    
    rms_ref = np.sqrt(np.mean(data_ref**2))
    rms_test = np.sqrt(np.mean(data_test**2))
    
    print(f"\n{title}:")
    print(f"  参考RMS: {rms_ref:.6f}")
    print(f"  测试RMS: {rms_test:.6f}")
    print(f"  RMS差异: {abs(rms_ref - rms_test):.6f} ({abs(rms_ref - rms_test)/rms_ref*100:.2f}%)")
    
    # 比较关键频率的能量
    for freq in [523, 1047, 1570]:
        idx = np.argmin(np.abs(freqs - freq))
        energy_ref = mag_ref[idx]
        energy_test = mag_test[idx]
        diff_pct = abs(energy_ref - energy_test) / max(energy_ref, 1e-10) * 100
        print(f"  {freq}Hz - 参考:{energy_ref:.2f}, 测试:{energy_test:.2f}, 差异:{diff_pct:.2f}%")
    
    return freqs[:2000], mag_ref[:2000], mag_test[:2000]

# 分析失败的测试
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

files = [
    ('tests/fixtures/osc_mix_tests/osc_mix_0.8080.wav', 
     'tests/output/test_osc_mix_0.8080.wav',
     'osc_mix=0.8080 (94.80%)'),
    ('tests/fixtures/osc_mix_tests/osc_mix_0.8502.wav',
     'tests/output/test_osc_mix_0.8502.wav',
     'osc_mix=0.8502 (94.91%)')
]

for i, (ref_file, test_file, title) in enumerate(files):
    freqs, mag_ref, mag_test = analyze_pair(ref_file, test_file, title)
    
    # 频谱对比
    axes[i, 0].plot(freqs, mag_ref, label='Reference', alpha=0.7)
    axes[i, 0].plot(freqs, mag_test, label='Test', alpha=0.7)
    axes[i, 0].set_xlabel('Frequency (Hz)')
    axes[i, 0].set_ylabel('Magnitude')
    axes[i, 0].set_title(f'Spectrum: {title}')
    axes[i, 0].legend()
    axes[i, 0].grid(True, alpha=0.3)
    
    # 差异
    axes[i, 1].plot(freqs, mag_ref - mag_test)
    axes[i, 1].set_xlabel('Frequency (Hz)')
    axes[i, 1].set_ylabel('Magnitude Difference')
    axes[i, 1].set_title(f'Difference: {title}')
    axes[i, 1].axhline(0, color='r', linestyle='--', alpha=0.5)
    axes[i, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('osc_mix_failed_analysis.png', dpi=150)
print("\n分析图表已保存到 osc_mix_failed_analysis.png")
