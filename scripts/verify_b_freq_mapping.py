#!/usr/bin/env python3
"""验证b_freq参数和实际频率的关系"""

import numpy as np
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import fft

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def find_fundamental(filepath):
    """找到音频的基频"""
    rate, data = load_wav(filepath)
    
    # 使用稳定段
    start_idx = int(1.0 * rate)
    end_idx = int(3.0 * rate)
    segment = data[start_idx:end_idx]
    
    # FFT
    fft_result = fft.rfft(segment)
    freqs = fft.rfftfreq(len(segment), 1/rate)
    magnitude = np.abs(fft_result)
    
    # 找峰值
    peak_idx = np.argmax(magnitude)
    return freqs[peak_idx]

def main():
    print("="*80)
    print("b_freq参数和实际频率分析")
    print("="*80)
    print(f"{'b_freq':<10} | {'Ref频率(Hz)':<15} | {'Gen频率(Hz)':<15} | {'频率差':<10}")
    print("-"*80)
    
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    # a_freq=0.5 对应 523Hz
    a_freq_hz = 523.0
    
    for b_freq_value in b_freq_values:
        ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
        gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
        
        if ref_file.exists() and gen_file.exists():
            ref_freq = find_fundamental(ref_file)
            gen_freq = find_fundamental(gen_file)
            freq_diff = abs(ref_freq - gen_freq)
            
            # 计算与a_freq的比率
            ref_ratio = ref_freq / a_freq_hz
            gen_ratio = gen_freq / a_freq_hz
            
            print(f"{b_freq_value:<10} | {ref_freq:<15.2f} | {gen_freq:<15.2f} | {freq_diff:<10.2f}")
            print(f"           | ratio={ref_ratio:.4f}    | ratio={gen_ratio:.4f}    |")
            print()

if __name__ == "__main__":
    main()
