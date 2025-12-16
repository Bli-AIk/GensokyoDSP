#!/usr/bin/env python3
"""详细分析失败测试的时域和频域特征"""
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

def compute_envelope(samples, window=1024):
    """计算包络"""
    envelope = []
    for i in range(0, len(samples), window//2):
        chunk = samples[i:i+window]
        if len(chunk) > 0:
            envelope.append(np.sqrt(np.mean(chunk**2)))
    return np.array(envelope)

def analyze_phase_correlation(ref_samples, test_samples):
    """分析相位相关性"""
    min_len = min(len(ref_samples), len(test_samples))
    ref = ref_samples[:min_len]
    test = test_samples[:min_len]
    
    # 计算互相关
    correlation = np.correlate(ref, test, mode='same')
    max_corr_idx = np.argmax(np.abs(correlation))
    lag = max_corr_idx - len(correlation) // 2
    
    # 计算相关系数
    corr_coef = np.corrcoef(ref, test)[0, 1]
    
    return lag, corr_coef

# 测试列表
tests = [
    ('b_freq_0.4958', 'b_freq'),
    ('b_freq_0.5506', 'b_freq'),
    ('b_freq_0.6519', 'b_freq'),
    ('b_freq_0.8080', 'b_freq'),
    ('b_freq_0.8502', 'b_freq'),
    ('b_freq_0.9051', 'b_freq'),
    ('a_noise_0.9515', 'a_noise'),
    ('a_noise_1.0', 'a_noise'),
]

print("=" * 100)
print("详细分析失败测试")
print("=" * 100)

for test_name, test_type in tests:
    ref_file = f"tests/fixtures/{test_type}_tests/{test_name}.wav"
    test_file = f"tests/output/test_{test_name}.wav"
    
    if not os.path.exists(ref_file) or not os.path.exists(test_file):
        print(f"\n{test_name}: 文件缺失")
        continue
    
    ref_samples, ref_sr = load_wav(ref_file)
    test_samples, test_sr = load_wav(test_file)
    
    # 包络分析
    ref_env = compute_envelope(ref_samples)
    test_env = compute_envelope(test_samples)
    
    min_env_len = min(len(ref_env), len(test_env))
    env_corr = np.corrcoef(ref_env[:min_env_len], test_env[:min_env_len])[0, 1]
    
    # 相位分析
    lag, phase_corr = analyze_phase_correlation(ref_samples, test_samples)
    
    # RMS对比
    ref_rms_total = np.sqrt(np.mean(ref_samples**2))
    test_rms_total = np.sqrt(np.mean(test_samples**2))
    
    # 分段RMS（起音、稳态、衰减）
    third = len(ref_samples) // 3
    ref_rms_attack = np.sqrt(np.mean(ref_samples[:third]**2))
    test_rms_attack = np.sqrt(np.mean(test_samples[:third]**2))
    ref_rms_sustain = np.sqrt(np.mean(ref_samples[third:2*third]**2))
    test_rms_sustain = np.sqrt(np.mean(test_samples[third:2*third]**2))
    ref_rms_decay = np.sqrt(np.mean(ref_samples[2*third:]**2))
    test_rms_decay = np.sqrt(np.mean(test_samples[2*third:]**2))
    
    print(f"\n{'='*100}")
    print(f"{test_name}:")
    print(f"  包络相关性: {env_corr:.4f}")
    print(f"  相位滞后: {lag} 样本 ({lag/ref_sr*1000:.2f} ms)")
    print(f"  相位相关性: {phase_corr:.4f}")
    print(f"  总RMS: 参考={ref_rms_total:.6f}, 测试={test_rms_total:.6f}, 比率={test_rms_total/ref_rms_total:.4f}")
    print(f"  起音RMS: 参考={ref_rms_attack:.6f}, 测试={test_rms_attack:.6f}, 比率={test_rms_attack/ref_rms_attack:.4f}")
    print(f"  稳态RMS: 参考={ref_rms_sustain:.6f}, 测试={test_rms_sustain:.6f}, 比率={test_rms_sustain/ref_rms_sustain:.4f}")
    print(f"  衰减RMS: 参考={ref_rms_decay:.6f}, 测试={test_rms_decay:.6f}, 比率={test_rms_decay/ref_rms_decay:.4f}")
    
    # 找出主要差异所在
    issues = []
    if abs(env_corr) < 0.5:
        issues.append("包络形状严重不匹配")
    if abs(lag) > ref_sr * 0.001:  # >1ms延迟
        issues.append(f"相位延迟 {lag/ref_sr*1000:.1f}ms")
    if abs(test_rms_attack/ref_rms_attack - 1.0) > 0.05:
        issues.append(f"起音能量差异 {(test_rms_attack/ref_rms_attack-1)*100:+.1f}%")
    if abs(test_rms_sustain/ref_rms_sustain - 1.0) > 0.05:
        issues.append(f"稳态能量差异 {(test_rms_sustain/ref_rms_sustain-1)*100:+.1f}%")
    
    if issues:
        print(f"  ⚠ 主要问题: {', '.join(issues)}")
    else:
        print(f"  ✓ 能量分布基本匹配")

print("\n" + "=" * 100)
