#!/usr/bin/env python3
"""
测试包络生成，看看是否与参考音频的RMS包络匹配
"""

import subprocess
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

def extract_envelope(data, sr, window_ms=10):
    """提取音频的包络"""
    window_samples = int(window_ms * sr / 1000)
    hop = window_samples // 2
    
    times = []
    envelope = []
    
    for i in range(0, len(data) - window_samples, hop):
        segment = data[i:i+window_samples]
        rms = np.sqrt(np.mean(segment**2))
        times.append(i / sr)
        envelope.append(rms)
    
    return np.array(times), np.array(envelope)

def main():
    """比较参考音频和测试音频的包络"""
    test_case = '0.8502'
    
    base_path = Path("/workspaces/GensokyoDSP")
    ref_file = base_path / "tests" / "fixtures" / "a_noise_tests" / f"a_noise_{test_case}.wav"
    test_file = base_path / "tests" / "output" / f"test_a_noise_{test_case}.wav"
    
    ref_data, ref_sr = read_wav(ref_file)
    test_data, test_sr = read_wav(test_file)
    
    # 提取包络
    ref_times, ref_env = extract_envelope(ref_data, ref_sr)
    test_times, test_env = extract_envelope(test_data, test_sr)
    
    print(f"a_noise={test_case} 包络对比:")
    print("=" * 70)
    print(f"{'时间(s)':<10} {'参考包络':<15} {'测试包络':<15} {'比例':<10}")
    print("-" * 70)
    
    # 前2秒，每100ms
    for t in np.arange(0, 2.0, 0.1):
        # 找最接近的时间点
        ref_idx = np.argmin(np.abs(ref_times - t))
        test_idx = np.argmin(np.abs(test_times - t))
        
        ref_val = ref_env[ref_idx]
        test_val = test_env[test_idx]
        ratio = test_val / ref_val if ref_val > 0.0001 else 0
        
        print(f"{t:<10.3f} {ref_val:<15.6f} {test_val:<15.6f} {ratio:<10.3f}")
    
    # 分析包络形状
    print("\n\n包络形状分析:")
    print("=" * 70)
    
    # 找到参考包络达到最大值50%的时间
    ref_max = np.max(ref_env)
    half_max_idx = np.where(ref_env >= ref_max * 0.5)[0]
    if len(half_max_idx) > 0:
        ref_half_max_time = ref_times[half_max_idx[0]]
        print(f"参考包络达到50%最大值的时间: {ref_half_max_time:.3f}秒")
    
    test_max = np.max(test_env)
    half_max_idx = np.where(test_env >= test_max * 0.5)[0]
    if len(half_max_idx) > 0:
        test_half_max_time = test_times[half_max_idx[0]]
        print(f"测试包络达到50%最大值的时间: {test_half_max_time:.3f}秒")
    
    # 计算起音时间（达到90%）
    ninety_idx_ref = np.where(ref_env >= ref_max * 0.9)[0]
    if len(ninety_idx_ref) > 0:
        ref_attack_time = ref_times[ninety_idx_ref[0]]
        print(f"参考包络起音时间(90%): {ref_attack_time:.3f}秒")
    
    ninety_idx_test = np.where(test_env >= test_max * 0.9)[0]
    if len(ninety_idx_test) > 0:
        test_attack_time = test_times[ninety_idx_test[0]]
        print(f"测试包络起音时间(90%): {test_attack_time:.3f}秒")

if __name__ == "__main__":
    main()
