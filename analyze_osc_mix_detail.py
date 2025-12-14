import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_audio_detail(filepath):
    rate, data = wavfile.read(filepath)
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    data = data.astype(np.float32) / 32768.0
    
    # 使用前0.1秒数据查看波形
    samples = data[:int(0.1 * rate)]
    
    # FFT整秒数据
    window_size = rate
    data_window = data[:window_size]
    window = np.hanning(len(data_window))
    data_windowed = data_window * window
    fft = np.fft.rfft(data_windowed)
    freqs = np.fft.rfftfreq(len(data_windowed), 1/rate)
    magnitude = np.abs(fft)
    
    return samples, freqs, magnitude, rate

# 比较开始、中间和结束时的osc_mix
test_files = ['osc_mix_0.0547.wav', 'osc_mix_0.5506.wav', 'osc_mix_1.0.wav']
osc_mix_dir = Path("tests/fixtures/osc_mix_tests")

fig, axes = plt.subplots(3, 2, figsize=(14, 10))

for i, filename in enumerate(test_files):
    filepath = osc_mix_dir / filename
    val_str = filename.replace('osc_mix_', '').replace('.wav', '')
    
    samples, freqs, magnitude, rate = analyze_audio_detail(filepath)
    
    # 波形图（前0.02秒）
    t = np.arange(len(samples[:int(0.02*rate)])) / rate
    axes[i, 0].plot(t, samples[:int(0.02*rate)])
    axes[i, 0].set_xlabel('Time (s)')
    axes[i, 0].set_ylabel('Amplitude')
    axes[i, 0].set_title(f'Waveform: osc_mix={val_str}')
    axes[i, 0].grid(True, alpha=0.3)
    
    # 频谱图（前2000Hz）
    axes[i, 1].plot(freqs[:2000], magnitude[:2000])
    axes[i, 1].set_xlabel('Frequency (Hz)')
    axes[i, 1].set_ylabel('Magnitude')
    axes[i, 1].set_title(f'Spectrum: osc_mix={val_str}')
    axes[i, 1].grid(True, alpha=0.3)
    
    # 标记预期频率
    axes[i, 1].axvline(523.25, color='r', linestyle='--', alpha=0.5, linewidth=1)
    axes[i, 1].axvline(880.0, color='b', linestyle='--', alpha=0.5, linewidth=1)
    
    # 找到前10个峰值
    peaks_idx = np.argsort(magnitude[:2000])[-10:][::-1]
    peaks_freq = freqs[peaks_idx]
    peaks_mag = magnitude[peaks_idx]
    
    print(f"\n{filename} - 前10个峰值频率:")
    for freq, mag in zip(peaks_freq, peaks_mag):
        print(f"  {freq:8.2f} Hz: {mag:10.2f}")

plt.tight_layout()
plt.savefig('osc_mix_waveform_detail.png', dpi=150)
print("\n波形和频谱已保存到 osc_mix_waveform_detail.png")

# 检查b_form=0.5对应的波形类型
print("\n根据文档:")
print("- a_form=0.0: 正弦波")
print("- b_form=0.5: 约等于锯齿波（0.57时为纯锯齿波）")
print("- a_freq=0.5 -> 523.25 Hz (C5)")
print("- b_freq=0.6875 -> 880 Hz (A5, 比C5高五度+小三度)")
