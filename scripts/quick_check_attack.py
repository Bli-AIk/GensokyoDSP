import numpy as np
import scipy.io.wavfile as wavfile
import sys

def measure_attack(filepath):
    try:
        rate, data = wavfile.read(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    if len(data.shape) > 1:
        data = data[:, 0]
    
    # Normalize
    data = data.astype(np.float32)
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data = data / max_val
    
    # Envelope follower (simple Hilbert or peak detection)
    # Here we just look at the absolute value for attack detection
    abs_data = np.abs(data)
    
    # Find peak index
    peak_idx = np.argmax(abs_data)
    peak_time = peak_idx / rate
    
    # Find start (e.g. 1% of peak)
    threshold = 0.01
    start_idx = np.where(abs_data > threshold)[0]
    if len(start_idx) > 0:
        start_time = start_idx[0] / rate
    else:
        start_time = 0.0
        
    print(f"File: {filepath}")
    print(f"Peak Time: {peak_time:.4f}s")
    print(f"Start Time: {start_time:.4f}s")
    print(f"Attack Duration (Start to Peak): {peak_time - start_time:.4f}s")

if __name__ == "__main__":
    measure_attack("tests/fixtures/a_freq_tests/a_freq_1.0.wav")
