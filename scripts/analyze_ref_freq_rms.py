#!/usr/bin/env python3
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

def analyze_freq(filepath):
    try:
        rate, data = wavfile.read(filepath)
    except:
        return 0, 0
    if len(data.shape) > 1:
        data = data[:, 0]
    # Normalize
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    else:
        data = data.astype(np.float32)

    # FFT to check freq
    window_size = min(rate, len(data))
    window = np.hanning(window_size)
    fft = np.fft.rfft(data[:window_size] * window)
    freqs = np.fft.rfftfreq(window_size, 1/rate)
    magnitude = np.abs(fft)
    
    peak_idx = np.argmax(magnitude)
    peak_freq = freqs[peak_idx]
    
    rms = np.sqrt(np.mean(data**2))
    
    return peak_freq, rms

print(f"{'a_freq':<10} {'Peak Hz':<10} {'RMS':<10}")
print("-" * 35)

files = sorted(Path('tests/fixtures/a_freq_tests').glob('a_freq_*.wav'))
results = []
for filepath in files:
    try:
        value_str = filepath.stem.replace('a_freq_', '')
        value = float(value_str)
        peak_freq, rms = analyze_freq(filepath)
        results.append((value, peak_freq, rms))
    except:
        pass

results.sort()
for val, freq, rms in results:
    print(f"{val:<10.4f} {freq:<10.2f} {rms:<10.6f}")
