import numpy as np
from scipy.io import wavfile
import sys

def analyze_file(filepath):
    try:
        sr, data = wavfile.read(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    data = data.astype(np.float64)
    if len(data.shape) > 1:
        data = data[:, 0]
    
    data /= 32768.0
    
    chunk_size = int(sr * 0.1) # 100ms
    times = []
    rms_values = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) == 0: break
        rms = np.sqrt(np.mean(chunk**2))
        rms_values.append(rms)
        times.append(i / sr)
        
    print(f"--- {filepath} ---")
    peak_rms = max(rms_values)
    print(f"Peak RMS: {peak_rms:.4f}")
    
    for t, r in zip(times, rms_values):
        if t <= 2.0:
             print(f"T={t:.1f}s RMS={r:.4f} ({r/peak_rms*100:.1f}%)")

analyze_file("tests/fixtures/vol_sus_tests/vol_sus_0.2518.wav")