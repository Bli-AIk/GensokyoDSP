import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

def analyze_freq(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    # FFT analysis on full data
    window_size = len(data)
    # Use closest power of 2 for efficiency if needed, but here accuracy is key.
    # rfft works on any size.
    window = np.hanning(window_size)
    fft = np.fft.rfft(data * window)
    freqs = np.fft.rfftfreq(window_size, 1/rate)
    magnitude = np.abs(fft)
    
    # 找到峰值频率 - remove limit
    peak_idx = np.argmax(magnitude[10:]) + 10
    
    # Parabolic interpolation
    y1 = magnitude[peak_idx - 1]
    y2 = magnitude[peak_idx]
    y3 = magnitude[peak_idx + 1]
    
    d = (y3 - y1) / (2 * (2 * y2 - y1 - y3))
    peak_freq = freqs[peak_idx] + d * (freqs[1] - freqs[0])
    
    rms = np.sqrt(np.mean(data**2))
    
    # Calculate THD (Total Harmonic Distortion + Noise)
    # Energy at peak +/- 5 bins
    peak_energy = np.sum(magnitude[peak_idx-5:peak_idx+6]**2)
    total_energy = np.sum(magnitude**2)
    thd = 1.0 - (peak_energy / total_energy)
    
    return peak_freq, rms, thd

# 分析所有a_freq文件
print(f"{'Value':<10} {'Freq(Hz)':<10} {'RMS':<10} {'THD':<10}")
for filepath in sorted(Path('tests/fixtures/a_freq_tests').glob('a_freq_*.wav')):
    value_str = filepath.stem.replace('a_freq_', '')
    try:
        value = float(value_str)
    except ValueError:
        continue
    
    peak_freq, rms, thd = analyze_freq(filepath)
    
    print(f"{value:<10.4f} {peak_freq:<10.2f} {rms:<10.6f} {thd:<10.6f}")
