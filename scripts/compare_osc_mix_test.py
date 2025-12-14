import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

def analyze(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    # 分析前1秒
    window_size = min(rate, len(data))
    data_window = data[:window_size]
    window = np.hanning(len(data_window))
    data_windowed = data_window * window
    
    fft = np.fft.rfft(data_windowed)
    freqs = np.fft.rfftfreq(len(data_windowed), 1/rate)
    magnitude = np.abs(fft)
    
    rms = np.sqrt(np.mean(data**2))
    
    return {
        'data': data[:int(0.05*rate)],
        'freqs': freqs,
        'magnitude': magnitude,
        'rms': rms,
        'rate': rate
    }

ref = analyze('tests/fixtures/osc_mix_tests/osc_mix_0.0547.wav')
test = analyze('tests/output/test_osc_mix_0.0547.wav')

print(f"参考音频 RMS: {ref['rms']:.6f}")
print(f"测试音频 RMS: {test['rms']:.6f}")
print(f"RMS差异: {abs(ref['rms'] - test['rms']):.6f}")

# 绘制对比
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 波形对比
t_ref = np.arange(len(ref['data'])) / ref['rate']
t_test = np.arange(len(test['data'])) / test['rate']

axes[0, 0].plot(t_ref, ref['data'], label='Reference', alpha=0.7)
axes[0, 0].plot(t_test, test['data'], label='Test', alpha=0.7)
axes[0, 0].set_xlabel('Time (s)')
axes[0, 0].set_ylabel('Amplitude')
axes[0, 0].set_title('Waveform Comparison (first 0.05s)')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 频谱对比（线性）
axes[0, 1].plot(ref['freqs'][:2000], ref['magnitude'][:2000], label='Reference', alpha=0.7)
axes[0, 1].plot(test['freqs'][:2000], test['magnitude'][:2000], label='Test', alpha=0.7)
axes[0, 1].set_xlabel('Frequency (Hz)')
axes[0, 1].set_ylabel('Magnitude')
axes[0, 1].set_title('Spectrum Comparison (0-2000Hz)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 频谱对比（dB）
ref_db = 20 * np.log10(ref['magnitude'] + 1e-10)
test_db = 20 * np.log10(test['magnitude'] + 1e-10)

axes[1, 0].plot(ref['freqs'][:2000], ref_db[:2000], label='Reference', alpha=0.7)
axes[1, 0].plot(test['freqs'][:2000], test_db[:2000], label='Test', alpha=0.7)
axes[1, 0].set_xlabel('Frequency (Hz)')
axes[1, 0].set_ylabel('Magnitude (dB)')
axes[1, 0].set_title('Spectrum Comparison (dB, 0-2000Hz)')
axes[1, 0].set_ylim(-60, 20)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 找到峰值频率对比
def find_peaks(freqs, magnitude, n=10):
    peaks_idx = np.argsort(magnitude[:2000])[-n:][::-1]
    return [(freqs[i], magnitude[i]) for i in peaks_idx]

ref_peaks = find_peaks(ref['freqs'], ref['magnitude'])
test_peaks = find_peaks(test['freqs'], test['magnitude'])

print("\n参考音频前5个峰值:")
for i, (f, m) in enumerate(ref_peaks[:5]):
    print(f"  {i+1}. {f:8.2f} Hz: {m:10.2f}")

print("\n测试音频前5个峰值:")
for i, (f, m) in enumerate(test_peaks[:5]):
    print(f"  {i+1}. {f:8.2f} Hz: {m:10.2f}")

# 显示差异
axes[1, 1].plot(ref['freqs'][:2000], ref_db[:2000] - test_db[:2000])
axes[1, 1].set_xlabel('Frequency (Hz)')
axes[1, 1].set_ylabel('Difference (dB)')
axes[1, 1].set_title('Spectrum Difference (Reference - Test)')
axes[1, 1].axhline(0, color='r', linestyle='--', alpha=0.5)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('osc_mix_comparison.png', dpi=150)
print("\n对比图表已保存到 osc_mix_comparison.png")
