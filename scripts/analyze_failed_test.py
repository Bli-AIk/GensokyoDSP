#!/usr/bin/env python3
import numpy as np
import scipy.io.wavfile as wavfile
import sys

def analyze(filepath):
    try:
        rate, data = wavfile.read(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    if len(data.shape) > 1:
        data = data[:, 0]
    
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    
    rms = np.sqrt(np.mean(data**2))
    peak = np.max(np.abs(data))
    
    print(f"File: {filepath}")
    print(f"RMS: {rms:.6f}")
    print(f"Peak: {peak:.6f}")

if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    files = ["tests/output/test_a_freq_0.9515.wav"]

for f in files:
    analyze(f)
