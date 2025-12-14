#!/usr/bin/env python3
"""测量实际的fade duration"""
import numpy as np
from scipy.io import wavfile

vals = ['0.8080', '0.8502', '0.9051', '0.9515', '1.0']

print('vol_fade | peak_time | fade_start (90%) | to 10% | fade_dur')
print('-' * 70)

for val in vals:
    filepath = f'tests/fixtures/vol_fade_tests/vol_fade_{val}.wav'
    sr, data = wavfile.read(filepath)
    
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    chunk_size = int(sr * 0.001)
    times = []
    rms_values = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) == 0:
            break
        rms = np.sqrt(np.mean(chunk**2))
        rms_values.append(rms)
        times.append(i / sr)
    
    times = np.array(times)
    rms_values = np.array(rms_values)
    peak = np.max(rms_values)
    peak_idx = np.argmax(rms_values)
    peak_time = times[peak_idx]
    
    # Fade start (90% of peak after peak)
    fade_start = None
    for i in range(peak_idx, len(rms_values)):
        if rms_values[i] < peak * 0.9:
            fade_start = times[i]
            break
    
    # To 10%
    to_10 = None
    for i in range(peak_idx, len(rms_values)):
        if rms_values[i] < peak * 0.1:
            to_10 = times[i]
            break
    
    if fade_start and to_10:
        fade_dur = to_10 - fade_start
        print(f'{val:8} | {peak_time:9.3f} | {fade_start:16.3f} | {to_10:6.3f} | {fade_dur:8.3f}')
    else:
        print(f'{val:8} | {peak_time:9.3f} | {"N/A":16} | {"N/A":6} | {"N/A":8}')
