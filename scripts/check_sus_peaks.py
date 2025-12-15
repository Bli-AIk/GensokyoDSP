#!/usr/bin/env python3
"""检查多个 vol_sus 测试的包络峰值时间"""

import numpy as np
from scipy.io import wavfile
import os

test_cases = [
    "0.0547", "0.1058", "0.1496", "0.2007", "0.2518", "0.3102", 
    "0.3540", "0.4051", "0.4536", "0.4958"
]

print("vol_sus 测试的包络峰值时间分析:")
print("=" * 70)

for case in test_cases:
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    
    if not os.path.exists(ref_file):
        print(f"vol_sus_{case}: 文件不存在")
        continue
    
    rate, data = wavfile.read(ref_file)
    
    # 转换为浮点数
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    
    # 创建包络
    window_size = 256
    env = np.array([np.sqrt(np.mean(data[max(0,i-window_size//2):min(len(data),i+window_size//2)]**2)) 
                    for i in range(0, len(data), window_size//4)])
    
    env_time = np.arange(len(env)) * (window_size/4) / rate
    
    # 找到峰值
    max_val = np.max(env)
    max_idx = np.argmax(env)
    peak_time = env_time[max_idx]
    
    # 找到 sustain 段 (在最大值之后)
    sus_start_idx = max_idx + 100
    sus_end_idx = min(sus_start_idx + 500, len(env) - 1)
    
    if sus_start_idx < len(env):
        sus_level = np.mean(env[sus_start_idx:sus_end_idx])
        sus_pct = (sus_level / max_val * 100.0) if max_val > 0 else 0
    else:
        sus_level = 0
        sus_pct = 0
    
    print(f"vol_sus_{case}:")
    print(f"  峰值时间: {peak_time:.3f}s")
    print(f"  峰值幅度: {max_val:.6f}")
    print(f"  Sustain 水平: {sus_level:.6f} ({sus_pct:.1f}% of peak)")
    print()

# 同时检查配置文件
print("\n检查配置文件中的 vol_atk 值:")
print("=" * 70)
for case in test_cases:
    config_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.ron"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            # 查找 vol_atk
            for line in content.split('\n'):
                if 'vol_atk:' in line:
                    print(f"vol_sus_{case}: {line.strip()}")
                    break
