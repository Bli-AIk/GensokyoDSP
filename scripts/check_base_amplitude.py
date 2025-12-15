#!/usr/bin/env python3
"""检查基础振荡器的幅度"""

import numpy as np
from scipy.io import wavfile

# 检查一个简单的测试案例 - vol_atk_0.0547
# 这个测试通过了，可以作为基准

ref_file = "tests/fixtures/vol_atk_tests/vol_atk_0.0547.wav"
out_file = "tests/output/test_vol_atk_0.0547.wav"

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

ref_max = np.max(ref_env)
out_max = np.max(out_env)

print(f"vol_atk_0.0547 (通过的测试):")
print(f"  参考峰值: {ref_max:.6f}")
print(f"  输出峰值: {out_max:.6f}")
print(f"  比例: {out_max/ref_max:.4f}")

# 检查绝对峰值
ref_peak = np.max(np.abs(ref_data))
out_peak = np.max(np.abs(out_data))
print(f"\n绝对峰值:")
print(f"  参考: {ref_peak:.6f}")
print(f"  输出: {out_peak:.6f}")
print(f"  比例: {out_peak/ref_peak:.4f}")

# 检查 vol_sus 测试
print(f"\n\nvol_sus 测试的峰值:")
print("=" * 60)

cases = ["0.0547", "0.1058", "0.1496", "0.2007", "0.2518", "0.3102"]

for case in cases:
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    out_file = f"tests/output/test_vol_sus_{case}.wav"
    
    try:
        ref_rate, ref_data = wavfile.read(ref_file)
        out_rate, out_data = wavfile.read(out_file)
        
        if ref_data.dtype == np.int16:
            ref_data = ref_data.astype(np.float32) / 32768.0
        if out_data.dtype == np.int16:
            out_data = out_data.astype(np.float32) / 32768.0
        
        ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                            for i in range(0, len(ref_data), window_size//4)])
        out_env = np.array([np.sqrt(np.mean(out_data[max(0,i-window_size//2):min(len(out_data),i+window_size//2)]**2)) 
                            for i in range(0, len(out_data), window_size//4)])
        
        ref_max = np.max(ref_env)
        out_max = np.max(out_env)
        
        print(f"vol_sus_{case}: ref={ref_max:.6f}, out={out_max:.6f}, ratio={out_max/ref_max:.4f}")
    except:
        pass
