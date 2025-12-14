import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from pathlib import Path

def get_energy_at_freq(freqs, magnitude, target_freq, bandwidth=10):
    """获取特定频率附近的能量"""
    mask = (freqs >= target_freq - bandwidth) & (freqs <= target_freq + bandwidth)
    return np.mean(magnitude[mask])

osc_mix_dir = Path("tests/fixtures/osc_mix_tests")
values = []
energy_523 = []
energy_880 = []
energy_1047 = []
rms_values = []

for filepath in sorted(osc_mix_dir.glob("osc_mix_*.wav")):
    val_str = filepath.stem.replace('osc_mix_', '')
    val = float(val_str)
    
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    # FFT
    window_size = min(rate, len(data))
    data_window = data[:window_size]
    window = np.hanning(len(data_window))
    data_windowed = data_window * window
    
    fft = np.fft.rfft(data_windowed)
    freqs = np.fft.rfftfreq(len(data_windowed), 1/rate)
    magnitude = np.abs(fft)
    
    values.append(val)
    energy_523.append(get_energy_at_freq(freqs, magnitude, 523))
    energy_880.append(get_energy_at_freq(freqs, magnitude, 880))
    energy_1047.append(get_energy_at_freq(freqs, magnitude, 1047))
    rms_values.append(np.sqrt(np.mean(data**2)))

# 绘制能量变化
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

axes[0].plot(values, energy_523, 'o-', label='523 Hz (Osc A基频)')
axes[0].plot(values, energy_880, 's-', label='880 Hz (预期Osc B)')
axes[0].plot(values, energy_1047, '^-', label='1047 Hz (2倍谐波)')
axes[0].set_xlabel('osc_mix')
axes[0].set_ylabel('Energy (linear)')
axes[0].set_title('Frequency Component Energy vs osc_mix')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(values, rms_values, 'o-')
axes[1].set_xlabel('osc_mix')
axes[1].set_ylabel('RMS')
axes[1].set_title('RMS vs osc_mix')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('osc_mix_energy_progression.png', dpi=150)
print("能量变化图已保存到 osc_mix_energy_progression.png")

# 打印数据
print("\nosc_mix值与各频率能量:")
print(f"{'osc_mix':<10} {'523Hz':<12} {'880Hz':<12} {'1047Hz':<12} {'RMS':<10}")
print("-" * 60)
for v, e523, e880, e1047, rms in zip(values, energy_523, energy_880, energy_1047, rms_values):
    print(f"{v:<10.4f} {e523:<12.2f} {e880:<12.2f} {e1047:<12.2f} {rms:<10.6f}")

print("\n观察:")
print("1. 880Hz的能量始终很低，这表明振荡器B可能不是880Hz")
print("2. 523Hz的能量基本保持不变")
print("3. 1047Hz（2倍谐波）的能量随osc_mix增加而增加")
print("4. 这暗示振荡器B可能是523Hz的锯齿波版本")
