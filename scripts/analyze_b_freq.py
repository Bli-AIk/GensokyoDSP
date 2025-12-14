import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

def get_peak_freq(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    window_size = min(rate, len(data))
    window = np.hanning(window_size)
    fft = np.fft.rfft(data[:window_size] * window)
    freqs = np.fft.rfftfreq(window_size, 1/rate)
    magnitude = np.abs(fft)
    
    peak_idx = np.argmax(magnitude[10:2000]) + 10
    return freqs[peak_idx]

print("b_freq测试（osc_mix=1.0，a_freq=0.5，b_form=0.5）")
print(f"{'b_freq值':<12} {'峰值频率(Hz)':<15}")
print("-" * 30)

for filepath in sorted(Path('tests/fixtures/b_freq_tests').glob('b_freq_*.wav')):
    value_str = filepath.stem.replace('b_freq_', '')
    value = float(value_str)
    
    peak_freq = get_peak_freq(filepath)
    
    # b_freq相对于a_freq的偏移
    offset_semitones = (value - 0.6875) * 48.0
    a_freq = 523.25  # a_freq=0.5时的频率
    expected_freq_old = a_freq * 2**(offset_semitones / 12.0)
    
    print(f"{value:<12.4f} {peak_freq:<15.2f} (预期: {expected_freq_old:.2f})")
