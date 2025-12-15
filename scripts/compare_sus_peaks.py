#!/usr/bin/env python3
"""比较所有 vol_sus 测试的峰值幅度"""

import numpy as np
from scipy.io import wavfile
import os

test_cases = [
    ("0.0", True),
    ("0.0547", True),
    ("0.1058", False),
    ("0.1496", False),
    ("0.2007", False),
    ("0.2518", True),
    ("0.3102", True),
    ("0.3540", True),
    ("0.4051", True),
    ("0.4536", True),
    ("0.4958", True),
    ("0.5506", True),
]

print("vol_sus 测试的峰值幅度对比:")
print("=" * 90)
print(f"{'Case':<15} {'Ref Peak':<12} {'Out Peak':<12} {'Ratio':<10} {'Ref Time':<12} {'Out Time':<12} {'Status':<10}")
print("=" * 90)

for case, passed in test_cases:
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    out_file = f"tests/output/test_vol_sus_{case}.wav"
    
    if not os.path.exists(ref_file) or not os.path.exists(out_file):
        continue
    
    ref_rate, ref_data = wavfile.read(ref_file)
    out_rate, out_data = wavfile.read(out_file)
    
    # 转换为浮点数
    if ref_data.dtype == np.int16:
        ref_data = ref_data.astype(np.float32) / 32768.0
    if out_data.dtype == np.int16:
        out_data = out_data.astype(np.float32) / 32768.0
    
    # 创建包络
    window_size = 256
    ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                        for i in range(0, len(ref_data), window_size//4)])
    out_env = np.array([np.sqrt(np.mean(out_data[max(0,i-window_size//2):min(len(out_data),i+window_size//2)]**2)) 
                        for i in range(0, len(out_data), window_size//4)])
    
    env_time = np.arange(len(ref_env)) * (window_size/4) / ref_rate
    
    ref_max = np.max(ref_env)
    out_max = np.max(out_env)
    ref_max_idx = np.argmax(ref_env)
    out_max_idx = np.argmax(out_env)
    ratio = out_max / ref_max if ref_max > 0 else 0
    
    status = "PASS" if passed else "FAIL"
    print(f"{case:<15} {ref_max:<12.6f} {out_max:<12.6f} {ratio:<10.4f} {env_time[ref_max_idx]:<12.3f} {env_time[out_max_idx]:<12.3f} {status:<10}")

print("\n峰值幅度比分析:")
print("通过的测试: 峰值幅度比应该接近 1.0 或一致")
print("失败的测试: 峰值幅度比 ~0.71, 说明 attack 曲线的增益不够")
