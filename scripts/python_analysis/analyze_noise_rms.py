#!/usr/bin/env python3
"""
分析a_noise测试的RMS趋势
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
        
        # 只分析第一声道
        if w.getnchannels() == 2:
            data = data[::2]
        
        # 取中间部分分析
        start = len(data) // 4
        end = len(data) * 3 // 4
        data = data[start:end]
        
        rms = math.sqrt(sum(x*x for x in data) / len(data))
        return rms

def main():
    # 分析a_noise测试
    fixtures = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures/a_noise_tests")
    
    noise_values = [
        0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 0.3540,
        0.4051, 0.4536, 0.4958, 0.5506, 0.6055, 0.6519, 0.7025,
        0.7489, 0.8080, 0.8502, 0.9051, 0.9515, 1.0
    ]
    
    print("a_noise测试的RMS分析:")
    print("="*60)
    print(f"{'a_noise':>10s}  {'RMS':>12s}")
    print("-"*60)
    
    for noise_val in noise_values:
        filename = f"a_noise_{noise_val}.wav" if noise_val != 1.0 else "a_noise_1.0.wav"
        filepath = fixtures / filename
        
        if filepath.exists():
            rms = get_rms(filepath)
            print(f"{noise_val:>10.4f}  {rms:>12.6f}")
    
    # 也分析a_color测试（应该都是a_noise=1.0）
    print("\n\na_color测试的RMS分析（a_noise=1.0）:")
    print("="*60)
    print(f"{'a_color':>10s}  {'RMS':>12s}")
    print("-"*60)
    
    color_fixtures = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures/a_color_tests")
    color_values = [0.0, 0.0547, 0.1058, 0.5, 1.0]
    
    for color_val in color_values:
        filename = f"a_color_{color_val}.wav" if color_val != 0.0 else "a_color_0.0.wav"
        filepath = color_fixtures / filename
        
        if filepath.exists():
            rms = get_rms(filepath)
            print(f"{color_val:>10.4f}  {rms:>12.6f}")

if __name__ == "__main__":
    main()
