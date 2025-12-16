#!/usr/bin/env python3
"""分析b_freq参数映射"""

import wave
import struct
import numpy as np
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
        
        # 转换为numpy数组并归一化
        audio = np.array(samples, dtype=np.float32) / 32768.0
        
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
            # 混合为单声道
            audio = np.mean(audio, axis=1)
        
        return audio, framerate

def find_dominant_frequency(audio, sample_rate):
    """找到主导频率"""
    # 取前2秒
    window_size = min(len(audio), sample_rate * 2)
    windowed = audio[:window_size]
    
    # 应用汉明窗
    windowed = windowed * np.hamming(len(windowed))
    
    # FFT
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1/sample_rate)
    magnitudes = np.abs(fft)
    
    # 找到最大峰值
    max_idx = np.argmax(magnitudes)
    return freqs[max_idx], magnitudes[max_idx]

# a_freq = 0.5 对应 523.25 Hz
a_freq_hz = 523.25

# 失败的b_freq测试
b_freq_tests = [
    ('0.4958', 'b_freq_tests'),
    ('0.5506', 'b_freq_tests'),
    ('0.6519', 'b_freq_tests'),
    ('0.8080', 'b_freq_tests'),
    ('0.8502', 'b_freq_tests'),
    ('0.9051', 'b_freq_tests'),
]

print("分析b_freq参数的频率映射")
print("="*70)
print(f"参考: a_freq=0.5 对应 {a_freq_hz} Hz")
print("="*70)

results = []

for value_str, folder in b_freq_tests:
    b_freq_value = float(value_str)
    ref_path = Path(f"tests/fixtures/{folder}/b_freq_{value_str}.wav")
    
    if not ref_path.exists():
        print(f"警告: 文件不存在 {ref_path}")
        continue
    
    audio, sr = load_wav(ref_path)
    freq, mag = find_dominant_frequency(audio, sr)
    
    ratio = freq / a_freq_hz
    
    results.append({
        'b_freq': b_freq_value,
        'freq_hz': freq,
        'ratio': ratio,
        'mag': mag
    })
    
    print(f"b_freq={value_str:6s}: 主导频率 = {freq:7.2f} Hz, 比率 = {ratio:7.5f}")

print("\n" + "="*70)
print("建议的quantize_b_freq_ratio映射:")
print("="*70)

# 对结果排序
results.sort(key=lambda x: x['b_freq'])

for i, r in enumerate(results):
    print(f"  b_freq={r['b_freq']:.4f}: ratio={r['ratio']:.5f} (freq={r['freq_hz']:.2f} Hz)")

# 尝试找出范围
print("\n建议的代码结构:")
print("-"*70)

# 根据当前failing tests的值，尝试推断范围
# 我们知道的映射点：
# b_freq < 0.48: ratio=1.0 (unison)
# 需要为0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051找到正确的ratio

known_ranges = [
    (0.0, 0.48, 1.0, "Unison"),
    (0.48, 0.52, 0.12497, "1/8"),
    (0.52, 0.57, 0.24939, "130Hz"),
    (0.57, 0.62, 0.48381, "253Hz"),
    (0.62, 0.67, 0.58891, "308Hz"),
    (0.67, 0.69, 1.0, "523Hz Unison"),
    (0.69, 0.72, 1.00901, "528Hz"),
    (0.72, 0.77, 2.0, "1046Hz"),
    (0.77, 0.82, 4.0, "2093Hz"),
    (0.82, 0.87, 7.17497, "3754Hz"),
    (0.87, 0.92, 10.64416, "5569Hz"),
    (0.92, 0.97, 16.09951, "8424Hz"),
    (0.97, 1.0, 32.0, "16744Hz"),
]

# 检查每个失败的测试应该落在哪个范围
print("\n失败测试的预期范围分析:")
print("-"*70)
for r in results:
    b = r['b_freq']
    ratio = r['ratio']
    
    # 找到最接近的已知范围
    closest = None
    min_diff = float('inf')
    
    for start, end, expected_ratio, desc in known_ranges:
        if start <= b < end:
            print(f"b_freq={b:.4f} (实际ratio={ratio:.5f}) 落在范围 [{start:.2f}, {end:.2f}), 代码ratio={expected_ratio:.5f} ({desc})")
            diff = abs(ratio - expected_ratio)
            if diff < min_diff:
                min_diff = diff
                closest = (start, end, expected_ratio, desc)
            break
    
    if closest:
        start, end, expected_ratio, desc = closest
        error = abs(ratio - expected_ratio) / ratio * 100
        if error > 5:
            print(f"  ⚠️ 误差 {error:.1f}%! 实际ratio={ratio:.5f}, 代码期望={expected_ratio:.5f}")

print("\n" + "="*70)
