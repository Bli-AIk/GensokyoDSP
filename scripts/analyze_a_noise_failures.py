#!/usr/bin/env python3
"""分析a_noise失败测试"""
import numpy as np
import wave
import struct
import os

def load_wav(filepath):
    """加载WAV文件"""
    with wave.open(filepath, 'rb') as wav:
        nchannels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        framerate = wav.getframerate()
        nframes = wav.getnframes()
        
        frames = wav.readframes(nframes)
        
        if sampwidth == 2:
            data = struct.unpack(f'{nframes * nchannels}h', frames)
        elif sampwidth == 4:
            data = struct.unpack(f'{nframes * nchannels}i', frames)
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")
        
        samples = np.array(data, dtype=float)
        
        if sampwidth == 2:
            samples = samples / 32768.0
        elif sampwidth == 4:
            samples = samples / 2147483648.0
        
        if nchannels == 2:
            samples = samples.reshape(-1, 2)
            samples = samples[:, 0]
        
        return samples, framerate

def calculate_steady_state_rms(samples, start_ratio=0.5):
    """计算稳态RMS（后半段）"""
    start = int(len(samples) * start_ratio)
    return np.sqrt(np.mean(samples[start:]**2))

def analyze_spectrum(samples, sr):
    """分析频谱"""
    fft = np.fft.rfft(samples)
    freqs = np.fft.rfftfreq(len(samples), 1.0/sr)
    power = np.abs(fft)
    
    # 计算频谱质心
    centroid = np.sum(freqs * power) / np.sum(power)
    
    # 找到峰值频率
    peak_idx = np.argmax(power)
    peak_freq = freqs[peak_idx]
    
    return {
        'centroid': centroid,
        'peak_freq': peak_freq,
        'power': power,
        'freqs': freqs
    }

# a_noise测试
a_noise_tests = [
    (0.9515, 'a_noise_0.9515'),
    (1.0, 'a_noise_1.0'),
]

print("=" * 80)
print("分析a_noise失败测试")
print("=" * 80)

for a_noise_val, test_name in a_noise_tests:
    ref_file = f"tests/fixtures/a_noise_tests/{test_name}.wav"
    test_file = f"tests/output/test_{test_name}.wav"
    
    if not os.path.exists(ref_file) or not os.path.exists(test_file):
        print(f"\n{test_name}: 文件缺失")
        continue
    
    ref_samples, ref_sr = load_wav(ref_file)
    test_samples, test_sr = load_wav(test_file)
    
    ref_steady = calculate_steady_state_rms(ref_samples)
    test_steady = calculate_steady_state_rms(test_samples)
    
    ratio = test_steady / ref_steady
    
    ref_spec = analyze_spectrum(ref_samples, ref_sr)
    test_spec = analyze_spectrum(test_samples, test_sr)
    
    print(f"\n{test_name} (a_noise={a_noise_val}):")
    print(f"  参考稳态RMS: {ref_steady:.6f}")
    print(f"  测试稳态RMS: {test_steady:.6f}")
    print(f"  测试/参考比率: {ratio:.4f}")
    print(f"  需要的补偿: {1.0/ratio:.4f}x")
    print(f"  参考频谱质心: {ref_spec['centroid']:.1f} Hz")
    print(f"  测试频谱质心: {test_spec['centroid']:.1f} Hz")
    print(f"  参考峰值频率: {ref_spec['peak_freq']:.1f} Hz")
    print(f"  测试峰值频率: {test_spec['peak_freq']:.1f} Hz")
    
    # 分析噪声能量分布
    # 计算不同频段的能量
    bands = [
        (0, 500, "低频(0-500Hz)"),
        (500, 2000, "中低频(500-2000Hz)"),
        (2000, 5000, "中高频(2000-5000Hz)"),
        (5000, 10000, "高频(5000-10000Hz)"),
    ]
    
    print(f"  频段能量分布:")
    for low, high, name in bands:
        # 使用较短的频谱作为基准
        min_len = min(len(ref_spec['freqs']), len(test_spec['freqs']))
        ref_freqs_used = ref_spec['freqs'][:min_len]
        test_freqs_used = test_spec['freqs'][:min_len]
        ref_power_used = ref_spec['power'][:min_len]
        test_power_used = test_spec['power'][:min_len]
        
        ref_mask = (ref_freqs_used >= low) & (ref_freqs_used < high)
        test_mask = (test_freqs_used >= low) & (test_freqs_used < high)
        
        ref_energy = np.sum(ref_power_used[ref_mask]**2)
        test_energy = np.sum(test_power_used[test_mask]**2)
        
        if ref_energy > 0:
            energy_ratio = test_energy / ref_energy
            print(f"    {name}: 测试/参考 = {energy_ratio:.4f}")

print("\n" + "=" * 80)
print("总结:")
print("  a_noise在高值时(0.9515, 1.0)需要减小broad_weight")
print("  测试输出RMS偏高，频谱质心偏高")
print("=" * 80)
