#!/usr/bin/env python3
"""对比通过和失败的b_freq测试"""

import numpy as np
import wave
import struct
from pathlib import Path

def load_wav(filepath):
    with wave.open(str(filepath), 'r') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        frames = wav_file.readframes(n_frames)
        
        if sample_width == 2:
            samples = struct.unpack(f'{n_frames * n_channels}h', frames)
        else:
            raise ValueError(f"不支持的采样宽度: {sample_width}")
        
        audio = np.array(samples, dtype=np.float32) / 32768.0
        
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
            audio = np.mean(audio, axis=1)
        
        return audio, framerate

def analyze_harmonics_ratio(audio, sample_rate, fundamental_freq):
    """分析谐波比率"""
    window_size = min(len(audio), sample_rate * 2)
    windowed = audio[:window_size]
    windowed = windowed * np.hamming(len(windowed))
    
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1/sample_rate)
    magnitudes = np.abs(fft)
    
    # 找到前4个谐波
    harmonics = []
    for n in range(1, 5):
        target_freq = fundamental_freq * n
        if target_freq > sample_rate / 2:
            break
        
        freq_range = 10.0
        mask = (freqs >= target_freq - freq_range) & (freqs <= target_freq + freq_range)
        if np.any(mask):
            idx = np.argmax(magnitudes[mask])
            actual_idx = np.where(mask)[0][idx]
            harmonics.append(magnitudes[actual_idx])
    
    # 计算相对于基频的比率
    if len(harmonics) > 0:
        h1 = harmonics[0]
        ratios = [h / h1 for h in harmonics]
        return ratios
    return []

# 测试用例：通过 vs 失败
test_cases = [
    # (name, fundamental_hz, status)
    ('0.0547', 65.4, 'pass'),
    ('0.1058', 121.9, 'pass'),
    ('0.1496', 523.0, 'pass'),
    ('0.4958', 65.5, 'fail'),
    ('0.5506', 130.5, 'fail'),
    ('0.6519', 308.0, 'fail'),
    ('0.8080', 2093.0, 'fail'),
    ('0.8502', 3754.0, 'fail'),
    ('0.9051', 5569.5, 'fail'),
]

print("="*80)
print("b_freq测试谐波比率分析 (相对于基频H1)")
print("="*80)
print(f"{'b_freq':<12} {'状态':<8} {'频率(Hz)':<12} {'H1':<8} {'H2':<8} {'H3':<8} {'H4':<8}")
print("-"*80)

for name, fundamental, status in test_cases:
    ref_path = Path(f"tests/fixtures/b_freq_tests/b_freq_{name}.wav")
    
    if not ref_path.exists():
        print(f"{name:<12} {status:<8} {fundamental:<12.1f} [文件不存在]")
        continue
    
    audio, sr = load_wav(ref_path)
    ratios = analyze_harmonics_ratio(audio, sr, fundamental)
    
    if len(ratios) >= 1:
        ratio_strs = [f"{r:.3f}" for r in ratios[:4]]
        while len(ratio_strs) < 4:
            ratio_strs.append("N/A")
        
        print(f"{name:<12} {status:<8} {fundamental:<12.1f} {ratio_strs[0]:<8} {ratio_strs[1]:<8} {ratio_strs[2]:<8} {ratio_strs[3]:<8}")

print("\n" + "="*80)
print("关键观察:")
print("  - 通过的测试应该显示一致的谐波比率模式")
print("  - 失败的测试可能显示不同的谐波衰减模式")
print("="*80)
