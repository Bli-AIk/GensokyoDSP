
import numpy as np
import soundfile as sf
import os
import glob

def get_peak_freq(file_path):
    data, sr = sf.read(file_path)
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # Use simple FFT
    fft = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1/sr)
    peak_idx = np.argmax(np.abs(fft))
    return freqs[peak_idx]

def extract_ratios():
    base_freq = 523.2511 # 440 * 2^((72-69)/12)
    files = sorted(glob.glob("tests/fixtures/b_freq_tests/*.wav"))
    
    print(f"Base Frequency: {base_freq:.4f} Hz")
    print("filename | freq | ratio")
    print("-" * 40)
    
    for f in files:
        freq = get_peak_freq(f)
        ratio = freq / base_freq
        name = os.path.basename(f)
        print(f"{name:20s} | {freq:8.2f} | {ratio:.5f}")

if __name__ == "__main__":
    extract_ratios()
