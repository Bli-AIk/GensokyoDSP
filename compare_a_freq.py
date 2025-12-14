import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

def analyze_audio(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    # 前0.05秒的波形
    samples = data[:int(0.05 * rate)]
    
    # FFT
    window_size = min(rate, len(data))
    window = np.hanning(window_size)
    fft = np.fft.rfft(data[:window_size] * window)
    freqs = np.fft.rfftfreq(window_size, 1/rate)
    magnitude = np.abs(fft)
    
    return samples, freqs, magnitude, rate

# 测试a_freq=0.5506
ref_samples, ref_freqs, ref_mag, ref_rate = analyze_audio('temps/a_freq/a_freq_0.5506.wav')
test_samples, test_freqs, test_mag, test_rate = analyze_audio('tests/output/test_a_freq_0.5506.wav')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 波形对比
t_ref = np.arange(len(ref_samples)) / ref_rate
t_test = np.arange(len(test_samples)) / test_rate

axes[0, 0].plot(t_ref, ref_samples, label='参考', alpha=0.7)
axes[0, 0].plot(t_test, test_samples, label='测试', alpha=0.7)
axes[0, 0].set_xlabel('时间 (s)')
axes[0, 0].set_ylabel('振幅')
axes[0, 0].set_title('波形对比 (前0.05秒)')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 频谱对比
axes[0, 1].plot(ref_freqs[:2000], ref_mag[:2000], label='参考', alpha=0.7)
axes[0, 1].plot(test_freqs[:2000], test_mag[:2000], label='测试', alpha=0.7)
axes[0, 1].set_xlabel('频率 (Hz)')
axes[0, 1].set_ylabel('幅度')
axes[0, 1].set_title('频谱对比 (0-2000Hz)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 找到峰值
ref_peak_idx = np.argmax(ref_mag[10:2000]) + 10
test_peak_idx = np.argmax(test_mag[10:2000]) + 10
ref_peak_freq = ref_freqs[ref_peak_idx]
test_peak_freq = test_freqs[test_peak_idx]

print(f"参考峰值频率: {ref_peak_freq:.2f} Hz")
print(f"测试峰值频率: {test_peak_freq:.2f} Hz")

# 预期频率
a_freq = 0.5506
midi_note = 72.0 + (a_freq - 0.5) * 48.0
expected_freq = 440.0 * 2**((midi_note - 69.0) / 12.0)
print(f"预期频率（根据当前算法）: {expected_freq:.2f} Hz")

# 频谱（dB）
ref_db = 20 * np.log10(ref_mag + 1e-10)
test_db = 20 * np.log10(test_mag + 1e-10)

axes[1, 0].plot(ref_freqs[:2000], ref_db[:2000], label='参考', alpha=0.7)
axes[1, 0].plot(test_freqs[:2000], test_db[:2000], label='测试', alpha=0.7)
axes[1, 0].set_xlabel('频率 (Hz)')
axes[1, 0].set_ylabel('幅度 (dB)')
axes[1, 0].set_title('频谱对比 (dB)')
axes[1, 0].set_ylim(-60, 20)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 差异
axes[1, 1].plot(ref_freqs[:2000], ref_db[:2000] - test_db[:2000])
axes[1, 1].set_xlabel('频率 (Hz)')
axes[1, 1].set_ylabel('差异 (dB)')
axes[1, 1].set_title('频谱差异')
axes[1, 1].axhline(0, color='r', linestyle='--', alpha=0.5)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('a_freq_comparison.png', dpi=150)
print("\n对比图已保存")
