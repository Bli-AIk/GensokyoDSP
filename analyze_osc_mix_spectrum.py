import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_spectrum(filepath):
    rate, data = wavfile.read(filepath)
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    data = data.astype(np.float32) / 32768.0
    
    # 使用前1秒数据
    window_size = rate
    data_window = data[:window_size]
    
    # 应用汉宁窗
    window = np.hanning(len(data_window))
    data_windowed = data_window * window
    
    # FFT
    fft = np.fft.rfft(data_windowed)
    freqs = np.fft.rfftfreq(len(data_windowed), 1/rate)
    magnitude = np.abs(fft)
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    return freqs, magnitude_db, rate

# 分析关键的osc_mix值
test_files = ['osc_mix_0.0547.wav', 'osc_mix_0.2518.wav', 'osc_mix_0.5506.wav', 
              'osc_mix_0.8080.wav', 'osc_mix_1.0.wav']
osc_mix_dir = Path("tests/fixtures/osc_mix_tests")

plt.figure(figsize=(14, 10))

for i, filename in enumerate(test_files):
    filepath = osc_mix_dir / filename
    val_str = filename.replace('osc_mix_', '').replace('.wav', '')
    
    freqs, magnitude_db, rate = analyze_spectrum(filepath)
    
    plt.subplot(3, 2, i+1)
    plt.plot(freqs[:5000], magnitude_db[:5000])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title(f'osc_mix = {val_str}')
    plt.grid(True, alpha=0.3)
    plt.ylim(-60, 0)
    
    # 标记关键频率
    expected_a = 523.25
    expected_b = 880.0
    plt.axvline(expected_a, color='r', linestyle='--', alpha=0.5, label=f'Osc A: {expected_a:.0f}Hz')
    plt.axvline(expected_b, color='b', linestyle='--', alpha=0.5, label=f'Osc B: {expected_b:.0f}Hz')
    plt.legend(fontsize=8)

plt.tight_layout()
plt.savefig('osc_mix_spectrum_detail.png', dpi=150)
print("频谱分析已保存到 osc_mix_spectrum_detail.png")

# 提取各个振荡器的能量
print("\n振荡器A和B的相对能量:")
print(f"{'osc_mix':<12} {'A能量(523Hz)':<20} {'B能量(880Hz)':<20} {'A/B比':<10}")
print("-" * 65)

all_files = sorted(osc_mix_dir.glob("osc_mix_*.wav"))
for filepath in all_files:
    val_str = filepath.stem.replace('osc_mix_', '')
    
    freqs, magnitude_db, rate = analyze_spectrum(filepath)
    
    # 找到523Hz和880Hz附近的能量（±10Hz）
    idx_a = np.argmin(np.abs(freqs - 523.25))
    idx_b = np.argmin(np.abs(freqs - 880.0))
    
    energy_a = magnitude_db[idx_a]
    energy_b = magnitude_db[idx_b]
    
    # 转换回线性以计算比例
    linear_a = 10**(energy_a/20)
    linear_b = 10**(energy_b/20)
    ratio = linear_a / linear_b if linear_b > 1e-10 else float('inf')
    
    print(f"{val_str:<12} {energy_a:<20.2f} {energy_b:<20.2f} {ratio:<10.4f}")

print("\n注意: osc_mix=0.0时应该只有振荡器A，osc_mix=1.0时应该只有振荡器B")
print("根据文档，在0.79时混合比例应该是50/50")
