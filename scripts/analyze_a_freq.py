import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

def analyze_freq(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    # FFT分析前1秒
    window_size = min(rate, len(data))
    window = np.hanning(window_size)
    fft = np.fft.rfft(data[:window_size] * window)
    freqs = np.fft.rfftfreq(window_size, 1/rate)
    magnitude = np.abs(fft)
    
    # 找到峰值频率
    peak_idx = np.argmax(magnitude[10:2000]) + 10
    peak_freq = freqs[peak_idx]
    
    rms = np.sqrt(np.mean(data**2))
    
    return peak_freq, rms

# 分析所有a_freq文件
print(f"{'a_freq值':<12} {'峰值频率(Hz)':<15} {'RMS':<10} {'预期频率(Hz)':<15}")
print("-" * 60)

for filepath in sorted(Path('temps/a_freq').glob('a_freq_*.wav')):
    value_str = filepath.stem.replace('a_freq_', '')
    value = float(value_str)
    
    peak_freq, rms = analyze_freq(filepath)
    
    # 计算预期频率
    midi_note = 72.0 + (value - 0.5) * 48.0
    expected_freq = 440.0 * 2**((midi_note - 69.0) / 12.0)
    
    print(f"{value:<12.4f} {peak_freq:<15.2f} {rms:<10.6f} {expected_freq:<15.2f}")
