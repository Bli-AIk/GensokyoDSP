#!/usr/bin/env python3
"""
分析特定失败测试的音频差异
"""

import numpy as np
import wave
import struct
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(str(filename), 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        # 读取所有帧
        frames = wav.readframes(n_frames)
        
        # 转换为numpy数组
        if sample_width == 2:  # 16-bit
            data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:  # 32-bit
            data = np.frombuffer(frames, dtype=np.int32)
        else:
            raise ValueError(f"不支持的采样位深: {sample_width}")
        
        # 转换为浮点数 [-1.0, 1.0]
        data = data.astype(np.float64) / (2**(sample_width * 8 - 1))
        
        # 如果是立体声，只取第一个声道
        if n_channels == 2:
            data = data[::2]
        
        return data, framerate

def analyze_audio(ref_file, test_file):
    """分析参考音频和测试音频的差异"""
    ref_data, ref_sr = read_wav(ref_file)
    test_data, test_sr = read_wav(test_file)
    
    print(f"参考音频: {ref_file.name}")
    print(f"  采样率: {ref_sr} Hz")
    print(f"  长度: {len(ref_data)} samples ({len(ref_data)/ref_sr:.3f} s)")
    print(f"  RMS: {np.sqrt(np.mean(ref_data**2)):.6f}")
    print(f"  峰值: {np.max(np.abs(ref_data)):.6f}")
    
    print(f"\n测试音频: {test_file.name}")
    print(f"  采样率: {test_sr} Hz")
    print(f"  长度: {len(test_data)} samples ({len(test_data)/test_sr:.3f} s)")
    print(f"  RMS: {np.sqrt(np.mean(test_data**2)):.6f}")
    print(f"  峰值: {np.max(np.abs(test_data)):.6f}")
    
    # 计算差异
    min_len = min(len(ref_data), len(test_data))
    ref_trim = ref_data[:min_len]
    test_trim = test_data[:min_len]
    
    diff = ref_trim - test_trim
    
    print(f"\n差异分析:")
    print(f"  RMS差异: {np.sqrt(np.mean(diff**2)):.6f}")
    print(f"  最大差异: {np.max(np.abs(diff)):.6f}")
    
    # 计算相关系数
    correlation = np.corrcoef(ref_trim, test_trim)[0, 1]
    print(f"  相关系数: {correlation:.6f}")
    
    # 按时间段分析
    segment_dur = 0.1  # 100ms segments
    segment_samples = int(segment_dur * ref_sr)
    n_segments = min_len // segment_samples
    
    print(f"\n按时间段分析 ({segment_dur*1000:.0f}ms段):")
    print(f"  {'时间(s)':<10} {'参考RMS':<12} {'测试RMS':<12} {'RMS差异':<12}")
    print("  " + "-" * 50)
    
    for i in range(min(10, n_segments)):  # 前10段
        start = i * segment_samples
        end = start + segment_samples
        
        ref_seg = ref_trim[start:end]
        test_seg = test_trim[start:end]
        
        ref_rms = np.sqrt(np.mean(ref_seg**2))
        test_rms = np.sqrt(np.mean(test_seg**2))
        diff_rms = abs(ref_rms - test_rms)
        
        print(f"  {i*segment_dur:<10.3f} {ref_rms:<12.6f} {test_rms:<12.6f} {diff_rms:<12.6f}")
    
    # 频谱分析
    print(f"\n频谱分析 (前1024样本):")
    fft_size = min(1024, min_len)
    ref_fft = np.fft.rfft(ref_trim[:fft_size])
    test_fft = np.fft.rfft(test_trim[:fft_size])
    
    ref_mag = np.abs(ref_fft)
    test_mag = np.abs(test_fft)
    
    # 找出最强的频率分量
    freqs = np.fft.rfftfreq(fft_size, 1/ref_sr)
    
    ref_top_idx = np.argsort(ref_mag)[-5:][::-1]
    test_top_idx = np.argsort(test_mag)[-5:][::-1]
    
    print(f"\n  参考音频主要频率成分:")
    for idx in ref_top_idx:
        print(f"    {freqs[idx]:.1f} Hz: 幅度 {ref_mag[idx]:.3f}")
    
    print(f"\n  测试音频主要频率成分:")
    for idx in test_top_idx:
        print(f"    {freqs[idx]:.1f} Hz: 幅度 {test_mag[idx]:.3f}")

def main():
    # 分析失败的测试
    test_cases = [
        ('a_noise', '0.8502'),
        ('a_noise', '0.9051'),
        ('a_noise', '0.9515'),
        ('a_noise', '1.0'),
        ('b_freq', '0.4958'),
        ('b_freq', '0.5506'),
        ('b_freq', '0.6519'),
        ('b_freq', '0.8080'),
        ('b_freq', '0.8502'),
        ('b_freq', '0.9051'),
        ('osc_mix', '0.8502'),
    ]
    
    base_path = Path("/workspaces/GensokyoDSP")
    
    for param, value in test_cases[:4]:  # 先分析前4个(a_noise)
        print("\n" + "=" * 70)
        print(f"分析: {param}={value}")
        print("=" * 70)
        
        ref_file = base_path / "tests" / "fixtures" / f"{param}_tests" / f"{param}_{value}.wav"
        test_file = base_path / "tests" / "output" / f"test_{param}_{value}.wav"
        
        if not ref_file.exists():
            print(f"参考文件不存在: {ref_file}")
            continue
        
        if not test_file.exists():
            print(f"测试文件不存在: {test_file}")
            continue
        
        analyze_audio(ref_file, test_file)

if __name__ == "__main__":
    main()
