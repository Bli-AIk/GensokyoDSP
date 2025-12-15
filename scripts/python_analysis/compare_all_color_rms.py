#!/usr/bin/env python3
"""
分析多个a_color值的RMS差异，找出最佳的noise gain调整
"""
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

output_dir = Path("/home/aik/rustProjects/GensokyoDSP/tests/output")
fixtures_dir = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures/a_color_tests")

color_values = [0.0, 0.0547, 0.1058, 0.5, 0.7489, 1.0]

print("a_color RMS比较:")
print("="*70)
print(f"{'a_color':>10s}  {'参考RMS':>12s}  {'输出RMS':>12s}  {'差异':>10s}  {'比率':>8s}")
print("-"*70)

total_ratio_error = 0
count = 0

for color_val in color_values:
    if color_val == 0.0:
        filename = "a_color_0.0.wav"
    elif color_val == int(color_val):
        filename = f"a_color_{int(color_val)}.0.wav"
    else:
        filename = f"a_color_{color_val}.wav"
    
    ref_file = fixtures_dir / filename
    out_file = output_dir / f"test_{ref_file.stem}.wav"
    
    if ref_file.exists() and out_file.exists():
        ref_rms = get_rms(ref_file)
        out_rms = get_rms(out_file)
        diff = abs(out_rms - ref_rms)
        ratio = out_rms / ref_rms if ref_rms > 1e-10 else 0.0
        
        print(f"{color_val:>10.4f}  {ref_rms:>12.6f}  {out_rms:>12.6f}  {diff:>10.6f}  {ratio:>7.4f}x")
        
        total_ratio_error += abs(ratio - 1.0)
        count += 1

if count > 0:
    avg_error = total_ratio_error / count
    print("="*70)
    print(f"平均比率误差: {avg_error:.4f}")
