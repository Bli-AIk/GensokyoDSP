#!/usr/bin/env python3
"""
测试ColoredNoise生成器的实际输出RMS
创建一个简单的测试来验证噪声生成器
"""

# 由于我们无法直接在Python中测试Rust代码，
# 让我们查看测试输出的噪声RMS和期望值之间的比率

import wave
import struct
import math
from pathlib import Path

def get_rms(filepath):
    """获取WAV文件的RMS值"""
    with wave.open(str(filepath), 'rb') as w:
        frames = w.readframes(w.getnframes())
        samples = struct.unpack(f'{len(frames)//2}h', frames)
        data = [s / 32768.0 for s in samples]
        
        if w.getnchannels() == 2:
            data = data[::2]
        
        start = len(data) // 4
        end = len(data) * 3 // 4
        data = data[start:end]
        
        rms = math.sqrt(sum(x*x for x in data) / len(data))
        return rms

# 比较参考和输出
output_dir = Path("/home/aik/rustProjects/GensokyoDSP/tests/output")
fixtures_dir = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures/a_color_tests")

ref_file = fixtures_dir / "a_color_0.0.wav"
out_file = output_dir / "test_a_color_0.0.wav"

ref_rms = get_rms(ref_file)
out_rms = get_rms(out_file)

ratio = out_rms / ref_rms

print(f"参考RMS: {ref_rms:.6f}")
print(f"输出RMS: {out_rms:.6f}")
print(f"比率: {ratio:.2f}x")
print(f"\n需要将噪声增益除以 {ratio:.2f} 来匹配参考")
print(f"或者乘以 {1.0/ratio:.4f}")
