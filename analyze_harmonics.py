#!/usr/bin/env python3
"""详细分析谐波内容"""

import numpy as np
import wave
import struct
from pathlib import Path

def load_wav(filepath):
    """加载WAV文件"""
    with wave.open(str(filepath), 'r') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        frames = wav_file.readframes(n_frames)
        
        if sample_width == 2:  # 16-bit
            samples = struct.unpack(f'{n_frames * n_channels}h', frames)
        else:
            raise ValueError(f"不支持的采样宽度: {sample_width}")
        
        audio = np.array(samples, dtype=np.float32) / 32768.0
        
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
            audio = np.mean(audio, axis=1)
        
        return audio, framerate

def analyze_harmonics(audio, sample_rate, fundamental_freq, name):
    """分析谐波结构"""
    # 使用2秒窗口
    window_size = min(len(audio), sample_rate * 2)
    windowed = audio[:window_size]
    windowed = windowed * np.hamming(len(windowed))
    
    # FFT
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1/sample_rate)
    magnitudes = np.abs(fft)
    
    # 找到谐波峰值
    harmonics = []
    for n in range(1, 21):  # 前20个谐波
        target_freq = fundamental_freq * n
        if target_freq > sample_rate / 2:
            break
        
        # 在目标频率附近寻找峰值（±10Hz）
        freq_range = 10.0
        mask = (freqs >= target_freq - freq_range) & (freqs <= target_freq + freq_range)
        if np.any(mask):
            idx = np.argmax(magnitudes[mask])
            actual_idx = np.where(mask)[0][idx]
            harmonics.append({
                'n': n,
                'expected_freq': target_freq,
                'actual_freq': freqs[actual_idx],
                'magnitude': magnitudes[actual_idx]
            })
    
    return harmonics

def compare_harmonics(ref_harmonics, test_harmonics, name):
    """比较参考和测试音频的谐波"""
    print(f"\n{'='*70}")
    print(f"谐波分析: {name}")
    print(f"{'='*70}")
    
    print(f"\n{'谐波':<8} {'参考幅度':<12} {'测试幅度':<12} {'差异%':<10} {'状态'}")
    print("-"*70)
    
    total_ref_energy = sum(h['magnitude']**2 for h in ref_harmonics)
    total_test_energy = sum(h['magnitude']**2 for h in test_harmonics)
    
    for i, (ref_h, test_h) in enumerate(zip(ref_harmonics, test_harmonics)):
        n = ref_h['n']
        ref_mag = ref_h['magnitude']
        test_mag = test_h['magnitude']
        
        if ref_mag > 0:
            diff_pct = (test_mag - ref_mag) / ref_mag * 100
        else:
            diff_pct = 0
        
        status = "✓" if abs(diff_pct) < 15 else "⚠"
        if abs(diff_pct) > 30:
            status = "✗"
        
        print(f"H{n:<7} {ref_mag:<12.2f} {test_mag:<12.2f} {diff_pct:>8.1f}%  {status}")
    
    print(f"\n总能量比较:")
    print(f"  参考: {total_ref_energy:.2f}")
    print(f"  测试: {total_test_energy:.2f}")
    print(f"  差异: {(total_test_energy - total_ref_energy) / total_ref_energy * 100:.1f}%")

# 失败的测试用例及其基频
test_cases = [
    ('b_freq_0.4958', 65.5),
    ('b_freq_0.5506', 130.5),
    ('b_freq_0.6519', 308.0),
    ('b_freq_0.8080', 2093.0),
    ('b_freq_0.8502', 3754.0),
    ('b_freq_0.9051', 5569.5),
]

for test_name, fundamental in test_cases:
    ref_path = Path(f"tests/fixtures/b_freq_tests/{test_name}.wav")
    test_path = Path(f"tests/output/test_{test_name}.wav")
    
    if not ref_path.exists() or not test_path.exists():
        print(f"跳过 {test_name}（文件不存在）")
        continue
    
    ref_audio, ref_sr = load_wav(ref_path)
    test_audio, test_sr = load_wav(test_path)
    
    ref_harmonics = analyze_harmonics(ref_audio, ref_sr, fundamental, "参考")
    test_harmonics = analyze_harmonics(test_audio, test_sr, fundamental, "测试")
    
    compare_harmonics(ref_harmonics, test_harmonics, test_name)

print("\n" + "="*70)
print("分析完成")
