#!/usr/bin/env python3
"""分析a_noise参考音频的实际权重"""

import wave
import numpy as np
from scipy import signal

def analyze_noise_content(file_path):
    """分析音频中的噪声含量"""
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
        
        # RMS
        rms = np.sqrt(np.mean(segment**2))
        
        # Peak
        peak = np.max(np.abs(segment))
        
        # 波峰因数
        crest_factor = peak / rms if rms > 0 else 0
        
        # 频谱分析
        fft = np.fft.rfft(segment)
        freqs = np.fft.rfftfreq(len(segment), 1/sr)
        magnitude = np.abs(fft)
        
        # 找基频（应该是523Hz for a_freq=0.5）
        fund_idx = np.argmin(np.abs(freqs - 523))
        fund_mag = magnitude[fund_idx]
        
        # 计算噪声能量（排除基频及其谐波）
        noise_indices = []
        for i, f in enumerate(freqs):
            # 排除基频的±50Hz范围
            is_fund_harmonic = False
            for h in range(1, 20):
                if abs(f - 523*h) < 50:
                    is_fund_harmonic = True
                    break
            if not is_fund_harmonic and f > 100:
                noise_indices.append(i)
        
        noise_mag = np.mean(magnitude[noise_indices])
        
        print(f"\n{file_path}:")
        print(f"  RMS: {rms:.6f}")
        print(f"  Peak: {peak:.6f}")
        print(f"  波峰因数: {crest_factor:.4f}")
        print(f"  基频幅度: {fund_mag:.1f}")
        print(f"  噪声平均幅度: {noise_mag:.1f}")
        print(f"  噪声/基频比: {noise_mag/fund_mag if fund_mag > 0 else 0:.6f}")
        
        return {
            'rms': rms,
            'peak': peak,
            'crest': crest_factor,
            'fund_mag': fund_mag,
            'noise_mag': noise_mag,
            'ratio': noise_mag/fund_mag if fund_mag > 0 else 0
        }

# 分析高噪声值案例
test_cases = [
    ('0.8080', 'tests/fixtures/a_noise_tests/a_noise_0.8080.wav', 
     'tests/output/test_a_noise_0.8080.wav'),
    ('0.8502', 'tests/fixtures/a_noise_tests/a_noise_0.8502.wav', 
     'tests/output/test_a_noise_0.8502.wav'),
    ('0.9051', 'tests/fixtures/a_noise_tests/a_noise_0.9051.wav', 
     'tests/output/test_a_noise_0.9051.wav'),
    ('0.9515', 'tests/fixtures/a_noise_tests/a_noise_0.9515.wav', 
     'tests/output/test_a_noise_0.9515.wav'),
    ('1.0', 'tests/fixtures/a_noise_tests/a_noise_1.0.wav', 
     'tests/output/test_a_noise_1.0.wav'),
]

print("="*80)
print("分析a_noise高值的噪声含量")
print("="*80)

for param, ref_path, test_path in test_cases:
    print(f"\n{'='*80}")
    print(f"a_noise = {param}")
    print(f"{'='*80}")
    print("参考文件:")
    ref_data = analyze_noise_content(ref_path)
    print("\n测试文件:")
    test_data = analyze_noise_content(test_path)
    print(f"\nRMS比率: {test_data['rms']/ref_data['rms']:.4f}")
    print(f"噪声/基频比率差异: {test_data['ratio'] - ref_data['ratio']:.6f}")
