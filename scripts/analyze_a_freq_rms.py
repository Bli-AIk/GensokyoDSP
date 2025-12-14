import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
import matplotlib.pyplot as plt

values = []
rms_list = []
peak_freqs = []

for filepath in sorted(Path('temps/a_freq').glob('a_freq_*.wav')):
    value_str = filepath.stem.replace('a_freq_', '')
    value = float(value_str)
    
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    rms = np.sqrt(np.mean(data**2))
    
    # 峰值频率
    window_size = min(rate, len(data))
    window = np.hanning(window_size)
    fft = np.fft.rfft(data[:window_size] * window)
    freqs = np.fft.rfftfreq(window_size, 1/rate)
    magnitude = np.abs(fft)
    peak_idx = np.argmax(magnitude[10:2000]) + 10
    peak_freq = freqs[peak_idx]
    
    values.append(value)
    rms_list.append(rms)
    peak_freqs.append(peak_freq)
    
    print(f"a_freq={value:.4f}: RMS={rms:.6f}, freq={peak_freq:.2f} Hz")

# 绘图
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

axes[0].plot(values, rms_list, 'o-')
axes[0].set_xlabel('a_freq')
axes[0].set_ylabel('RMS')
axes[0].set_title('RMS vs a_freq')
axes[0].grid(True, alpha=0.3)
axes[0].axhline(0.056, color='r', linestyle='--', alpha=0.5, label='~0.056 baseline')
axes[0].legend()

axes[1].plot(values, peak_freqs, 'o-')
axes[1].set_xlabel('a_freq')
axes[1].set_ylabel('Peak Frequency (Hz)')
axes[1].set_title('Frequency vs a_freq')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('a_freq_rms_analysis.png', dpi=150)
print("\n分析图已保存")

print(f"\nRMS范围: {min(rms_list):.6f} - {max(rms_list):.6f}")
print(f"RMS平均: {np.mean(rms_list):.6f}")
print(f"RMS标准差: {np.std(rms_list):.6f}")
