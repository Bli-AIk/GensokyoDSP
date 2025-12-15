#!/usr/bin/env python3
import numpy as np
from scipy.io import wavfile
import glob
import os

def get_rms(filepath):
    try:
        sr, data = wavfile.read(filepath)
        if data.dtype == np.int16:
            data = data.astype(np.float64) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float64) / 2147483648.0
        else:
            data = data.astype(np.float64)
        if len(data.shape) > 1:
            data = data[:, 0]
        return np.sqrt(np.mean(data**2))
    except Exception as e:
        print(f"Error {filepath}: {e}")
        return 0.0

files = glob.glob("tests/fixtures/a_noise_tests/a_noise_*.wav")
results = []

for f in files:
    val_str = f.split('_')[-1].replace('.wav', '')
    try:
        val = float(val_str)
        rms = get_rms(f)
        results.append((val, rms))
    except:
        pass

results.sort()

print("Reference RMS Trend:")
print("a_noise | RMS")
for val, rms in results:
    print(f"{val:7.4f} | {rms:.6f}")