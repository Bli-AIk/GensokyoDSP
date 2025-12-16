#!/usr/bin/env python3
"""详细比较b_freq测试的谐波能量分布"""

import wave
import numpy as np

def analyze_harmonics(file_path, fund_freq, max_harm=10):
    """分析指定频率的前N个谐波"""
    with wave.open(file_path, 'r') as wav:
        sr = wav.getframerate()
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        
        if wav.getnchannels() == 2:
            data = data.reshape(-1, 2)[:, 0]
        
        # 使用稳定段
        start = int(sr * 1.0)
        end = int(sr * 3.0)
        segment = data[start:end]
        
        # FFT
        fft = np.fft.rfft(segment)
        freqs = np.fft.rfftfreq(len(segment), 1/sr)
        magnitude = np.abs(fft)
        
        # 分析每个谐波
        harmonics = []
        for h in range(1, max_harm+1):
            target_freq = fund_freq * h
            if target_freq > sr/2:
                break
            # 在±10Hz范围内找峰值
            idx_min = np.argmin(np.abs(freqs - (target_freq - 10)))
            idx_max = np.argmin(np.abs(freqs - (target_freq + 10)))
            harm_mag = np.max(magnitude[idx_min:idx_max+1])
            harmonics.append((h, target_freq, harm_mag))
        
        return harmonics, np.sqrt(np.mean(segment**2))

# 测试案例
test_cases = [
    (0.4958, 65.0, 10),
    (0.5506, 130.0, 8),
    (0.6519, 308.0, 6),
    (0.8080, 2093.0, 4),
    (0.8502, 3754.0, 3),
    (0.9051, 5570.0, 2),
]

for b_freq_param, fund_freq, max_harm in test_cases:
    ref_path = f'tests/fixtures/b_freq_tests/b_freq_{b_freq_param}.wav'
    test_path = f'tests/output/test_b_freq_{b_freq_param}.wav'
    
    print(f"\n{'='*80}")
    print(f"b_freq={b_freq_param} (基频: {fund_freq} Hz)")
    print(f"{'='*80}")
    
    ref_harms, ref_rms = analyze_harmonics(ref_path, fund_freq, max_harm)
    test_harms, test_rms = analyze_harmonics(test_path, fund_freq, max_harm)
    
    print(f"\nRMS: 参考={ref_rms:.6f}, 测试={test_rms:.6f}, 比率={test_rms/ref_rms:.4f}")
    print(f"\n谐波分析:")
    print(f"{'谐波':<6} {'频率':<8} {'参考幅度':<12} {'测试幅度':<12} {'比率':<8}")
    print("-" * 60)
    
    for i in range(len(ref_harms)):
        h_ref = ref_harms[i]
        h_test = test_harms[i]
        ratio = h_test[2] / h_ref[2] if h_ref[2] > 0 else 0
        print(f"{h_ref[0]:<6} {h_ref[1]:<8.0f} {h_ref[2]:<12.1f} {h_test[2]:<12.1f} {ratio:<8.4f}")
    
    # 计算谐波能量比
    ref_total = sum(h[2] for h in ref_harms)
    test_total = sum(h[2] for h in test_harms)
    print(f"\n总谐波能量: 参考={ref_total:.1f}, 测试={test_total:.1f}, 比率={test_total/ref_total:.4f}")
