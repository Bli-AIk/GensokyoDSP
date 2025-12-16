#!/usr/bin/env python3
"""分析失败的测试案例"""

import wave
import numpy as np
import os

def analyze_wav(file_path):
    """分析WAV文件并返回详细信息"""
    with wave.open(file_path, 'r') as wav:
        sr = wav.getframerate()
        n_channels = wav.getnchannels()
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        
        if n_channels == 2:
            data = data.reshape(-1, 2)[:, 0]  # 只取左声道
        
        return {
            'sr': sr,
            'duration': n_frames / sr,
            'data': data,
            'rms': np.sqrt(np.mean(data**2)),
            'peak': np.max(np.abs(data)),
            'mean': np.mean(data),
            'std': np.std(data)
        }

def compare_files(ref_path, test_path):
    """比较两个音频文件"""
    if not os.path.exists(ref_path):
        return f"参考文件不存在: {ref_path}"
    if not os.path.exists(test_path):
        return f"测试文件不存在: {test_path}"
    
    ref = analyze_wav(ref_path)
    test = analyze_wav(test_path)
    
    # 计算差异
    if len(ref['data']) != len(test['data']):
        return f"长度不匹配: {len(ref['data'])} vs {len(test['data'])}"
    
    diff = ref['data'] - test['data']
    correlation = np.corrcoef(ref['data'], test['data'])[0, 1]
    
    result = f"""
文件: {os.path.basename(ref_path)}
参考RMS: {ref['rms']:.6f}
测试RMS: {test['rms']:.6f}
RMS比率: {test['rms']/ref['rms']:.4f}
参考Peak: {ref['peak']:.6f}
测试Peak: {test['peak']:.6f}
差异RMS: {np.sqrt(np.mean(diff**2)):.6f}
相关性: {correlation:.4f}
相似度估计: {correlation * 100:.2f}%
"""
    return result

# 失败的测试案例
failed_tests = [
    ('a_noise', '0.9515'),
    ('a_noise', '1.0'),
    ('b_freq', '0.4958'),
    ('b_freq', '0.5506'),
    ('b_freq', '0.6519'),
    ('b_freq', '0.8080'),
    ('b_freq', '0.8502'),
    ('b_freq', '0.9051'),
]

print("=" * 80)
print("分析失败的测试案例")
print("=" * 80)

for param, value in failed_tests:
    filename = f"{param}_{value}.wav"
    ref_path = f"tests/fixtures/{param}_tests/{filename}"
    test_path = f"tests/output/test_{param}_{value}.wav"
    
    print(f"\n{'='*80}")
    print(compare_files(ref_path, test_path))
