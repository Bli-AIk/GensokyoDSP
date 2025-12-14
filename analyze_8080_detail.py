import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

def load_wav(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

# 加载文件
rate_ref, data_ref = load_wav('tests/fixtures/osc_mix_tests/osc_mix_0.8080.wav')
rate_test, data_test = load_wav('tests/output/test_osc_mix_0.8080.wav')

# 频谱分析
window_size = min(rate_ref, len(data_ref))
window = np.hanning(window_size)

fft_ref = np.fft.rfft(data_ref[:window_size] * window)
fft_test = np.fft.rfft(data_test[:window_size] * window)

freqs = np.fft.rfftfreq(window_size, 1/rate_ref)
mag_ref = np.abs(fft_ref)
mag_test = np.abs(fft_test)

# 绘制对比
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 波形
axes[0, 0].plot(np.arange(4800) / rate_ref, data_ref[:4800], label='Ref', alpha=0.7)
axes[0, 0].plot(np.arange(4800) / rate_test, data_test[:4800], label='Test', alpha=0.7)
axes[0, 0].set_xlabel('Time (s)')
axes[0, 0].set_ylabel('Amplitude')
axes[0, 0].set_title('Waveform (0.1s)')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 频谱（线性，0-2000Hz）
axes[0, 1].plot(freqs[:2000], mag_ref[:2000], label='Ref', alpha=0.7)
axes[0, 1].plot(freqs[:2000], mag_test[:2000], label='Test', alpha=0.7)
axes[0, 1].set_xlabel('Frequency (Hz)')
axes[0, 1].set_ylabel('Magnitude')
axes[0, 1].set_title('Spectrum (0-2000Hz)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 频谱（dB）
mag_ref_db = 20 * np.log10(mag_ref + 1e-10)
mag_test_db = 20 * np.log10(mag_test + 1e-10)

axes[1, 0].plot(freqs[:2000], mag_ref_db[:2000], label='Ref', alpha=0.7)
axes[1, 0].plot(freqs[:2000], mag_test_db[:2000], label='Test', alpha=0.7)
axes[1, 0].set_xlabel('Frequency (Hz)')
axes[1, 0].set_ylabel('Magnitude (dB)')
axes[1, 0].set_title('Spectrum (dB)')
axes[1, 0].set_ylim(-60, 20)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 频谱差异
axes[1, 1].plot(freqs[:2000], mag_ref_db[:2000] - mag_test_db[:2000])
axes[1, 1].set_xlabel('Frequency (Hz)')
axes[1, 1].set_ylabel('Difference (dB)')
axes[1, 1].set_title('Spectrum Difference')
axes[1, 1].axhline(0, color='r', linestyle='--', alpha=0.5)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('osc_mix_8080_detail.png', dpi=150)
print("详细对比图已保存")

# 打印统计
print(f"\nRMS:")
print(f"  参考: {np.sqrt(np.mean(data_ref**2)):.6f}")
print(f"  测试: {np.sqrt(np.mean(data_test**2)):.6f}")

print(f"\n关键频率能量:")
for freq in [523, 1047, 1570]:
    idx = np.argmin(np.abs(freqs - freq))
    print(f"  {freq}Hz: 参考={mag_ref[idx]:.2f}, 测试={mag_test[idx]:.2f}, " 
          f"比率={mag_test[idx]/mag_ref[idx]:.4f}")
