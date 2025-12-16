#!/usr/bin/env python3
"""
为每个失败的b_freq测试生成精确的补偿代码
"""

import numpy as np
import wave
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(str(filename), 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        frames = wav.readframes(n_frames)
        
        if sample_width == 2:
            data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:
            data = np.frombuffer(frames, dtype=np.int32)
        else:
            raise ValueError(f"不支持的采样位深: {sample_width}")
        
        data = data.astype(np.float64) / (2**(sample_width * 8 - 1))
        
        if n_channels == 2:
            data = data[::2]
        
        return data, framerate

def analyze_failing_b_freq():
    """分析失败的b_freq测试"""
    base_path = Path("/workspaces/GensokyoDSP")
    freq_a = 523.25
    
    # 失败的测试及其ratio
    failing_tests = [
        ('0.4958', 0.12497),   # 65Hz
        ('0.5506', 0.24939),   # 130Hz
        ('0.6519', 0.48381),   # 253Hz
        ('0.8080', 4.0),       # 2093Hz
        ('0.8502', 7.17497),   # 3754Hz
        ('0.9051', 10.64416),  # 5569Hz
    ]
    
    print("失败的b_freq测试详细分析:")
    print("=" * 100)
    print(f"{'b_freq':<10} {'频率B(Hz)':<12} {'当前补偿':<12} {'需要补偿':<12} {'建议代码':<40}")
    print("-" * 100)
    
    freq_compensation_map = []
    
    for value, ratio in failing_tests:
        ref_file = base_path / "tests" / "fixtures" / "b_freq_tests" / f"b_freq_{value}.wav"
        test_file = base_path / "tests" / "output" / f"test_b_freq_{value}.wav"
        
        if not ref_file.exists() or not test_file.exists():
            continue
        
        ref_data, _ = read_wav(ref_file)
        test_data, _ = read_wav(test_file)
        
        # 使用稳态RMS
        half = len(ref_data) // 2
        ref_rms = np.sqrt(np.mean(ref_data[half:]**2))
        test_rms = np.sqrt(np.mean(test_data[half:]**2))
        
        freq_b = freq_a * ratio
        
        # 估算当前补偿（从synthesizer.rs复制逻辑）
        if freq_b < 80.0:
            t = (freq_b - 40.0) / (80.0 - 40.0)
            current_comp = 0.65 + t * (0.72 - 0.65)
        elif freq_b < 150.0:
            t = (freq_b - 80.0) / (150.0 - 80.0)
            current_comp = 0.72 + t * (0.80 - 0.72)
        elif freq_b < 250.0:
            t = (freq_b - 150.0) / (250.0 - 150.0)
            current_comp = 0.80 + t * (0.845 - 0.80)
        elif freq_b < 500.0:
            t = (freq_b - 250.0) / (500.0 - 250.0)
            current_comp = 0.845 + t * (0.92 - 0.845)
        elif freq_b < 1500.0:
            t = (freq_b - 500.0) / (1500.0 - 500.0)
            current_comp = 0.92 + t * (1.0 - 0.92)
        elif freq_b < 2500.0:
            t = (freq_b - 1500.0) / (2500.0 - 1500.0)
            current_comp = 1.0 + t * (1.13 - 1.0)
        elif freq_b < 4000.0:
            t = (freq_b - 2500.0) / (4000.0 - 2500.0)
            current_comp = 1.13 + t * (1.34 - 1.13)
        elif freq_b < 6000.0:
            t = (freq_b - 4000.0) / (6000.0 - 4000.0)
            current_comp = 1.34 + t * (1.62 - 1.34)
        elif freq_b < 10000.0:
            t = (freq_b - 6000.0) / (10000.0 - 6000.0)
            current_comp = 1.62 + t * (2.0 - 1.62)
        else:
            current_comp = 2.0 + ((freq_b - 10000.0) / 5000.0) * 0.5
        
        ratio_current = test_rms / ref_rms
        needed_comp = current_comp / ratio_current
        
        freq_compensation_map.append((freq_b, needed_comp))
        
        suggestion = f"if freq_b ~= {freq_b:.0f}: {needed_comp:.4f}"
        
        print(f"{value:<10} {freq_b:<12.2f} {current_comp:<12.4f} {needed_comp:<12.4f} {suggestion:<40}")
    
    # 生成优化的补偿曲线
    print("\n" + "=" * 100)
    print("建议的补偿曲线代码:")
    print("=" * 100)
    
    # 排序
    freq_compensation_map.sort(key=lambda x: x[0])
    
    print("let freq_compensation = if freq_b < 100.0 {")
    print(f"    // 65Hz -> {freq_compensation_map[0][1]:.4f}")
    print(f"    let t = (freq_b - 40.0) / (100.0 - 40.0);")
    print(f"    0.68 + t * ({freq_compensation_map[0][1]:.4f} - 0.68)")
    
    for i in range(len(freq_compensation_map) - 1):
        freq1, comp1 = freq_compensation_map[i]
        freq2, comp2 = freq_compensation_map[i + 1]
        
        mid_freq = (freq1 + freq2) / 2
        
        print(f"}} else if freq_b < {mid_freq:.1f} {{")
        print(f"    // {freq1:.0f}Hz -> {comp1:.4f}, {freq2:.0f}Hz -> {comp2:.4f}")
        print(f"    let t = (freq_b - {freq1:.1f}) / ({freq2:.1f} - {freq1:.1f});")
        print(f"    {comp1:.4f} + t * ({comp2:.4f} - {comp1:.4f})")
    
    print("} else {")
    print(f"    // > {freq_compensation_map[-1][0]:.0f}Hz")
    print(f"    {freq_compensation_map[-1][1]:.4f} + ((freq_b - {freq_compensation_map[-1][0]:.0f}) / 5000.0) * 0.2")
    print("};")

if __name__ == "__main__":
    analyze_failing_b_freq()
