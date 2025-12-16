#!/usr/bin/env python3
"""分析b_freq测试的频谱"""

import wave
import numpy as np
from scipy import signal

def analyze_frequency(file_path):
    """分析音频文件的主频率"""
    with wave.open(file_path, 'r') as wav:
        sr = wav.getframerate()
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        
        if wav.getnchannels() == 2:
            data = data.reshape(-1, 2)[:, 0]
        
        # 使用中间部分的稳定信号
        start = int(sr * 1.0)
        end = int(sr * 2.0)
        segment = data[start:end]
        
        # FFT分析
        fft = np.fft.rfft(segment)
        freqs = np.fft.rfftfreq(len(segment), 1/sr)
        magnitude = np.abs(fft)
        
        # 找到峰值频率
        peak_idx = np.argmax(magnitude[1:]) + 1  # 跳过DC
        peak_freq = freqs[peak_idx]
        
        # 找到前5个峰值
        peaks_idx = signal.find_peaks(magnitude, height=np.max(magnitude)*0.1)[0]
        top_peaks = sorted(peaks_idx, key=lambda i: magnitude[i], reverse=True)[:5]
        
        print(f"\n文件: {file_path}")
        print(f"主频率: {peak_freq:.2f} Hz")
        print(f"前5个峰值:")
        for i, idx in enumerate(top_peaks, 1):
            print(f"  {i}. {freqs[idx]:.2f} Hz (幅度: {magnitude[idx]:.0f})")
        
        return peak_freq

# 测试失败的b_freq案例
test_cases = [
    ('0.4958', 'tests/fixtures/b_freq_tests/b_freq_0.4958.wav', 
     'tests/output/test_b_freq_0.4958.wav'),
    ('0.5506', 'tests/fixtures/b_freq_tests/b_freq_0.5506.wav', 
     'tests/output/test_b_freq_0.5506.wav'),
    ('0.6519', 'tests/fixtures/b_freq_tests/b_freq_0.6519.wav', 
     'tests/output/test_b_freq_0.6519.wav'),
    ('0.8080', 'tests/fixtures/b_freq_tests/b_freq_0.8080.wav', 
     'tests/output/test_b_freq_0.8080.wav'),
    ('0.8502', 'tests/fixtures/b_freq_tests/b_freq_0.8502.wav', 
     'tests/output/test_b_freq_0.8502.wav'),
    ('0.9051', 'tests/fixtures/b_freq_tests/b_freq_0.9051.wav', 
     'tests/output/test_b_freq_0.9051.wav'),
]

print("="*80)
print("分析b_freq测试的频谱")
print("="*80)

for param, ref_path, test_path in test_cases:
    print(f"\n{'='*80}")
    print(f"b_freq = {param}")
    print(f"{'='*80}")
    print("参考文件:")
    ref_freq = analyze_frequency(ref_path)
    print("\n测试文件:")
    test_freq = analyze_frequency(test_path)
    print(f"\n频率比率: {test_freq/ref_freq:.4f}")
    
    # 计算期望的频率（基于a_freq=0.5=523Hz）
    print(f"\na_freq=0.5 -> 523 Hz")
    print(f"参考频率: {ref_freq:.2f} Hz -> b_freq比率: {ref_freq/523:.4f}")
