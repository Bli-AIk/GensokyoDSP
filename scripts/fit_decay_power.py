#!/usr/bin/env python3
"""分析不同 vol_sus 值的最佳 decay_power"""

import numpy as np
from scipy.io import wavfile
from scipy.optimize import minimize_scalar

cases = [
    ("0.0547", 0.096),
    ("0.1058", 0.317),
    ("0.1496", 0.489),
    ("0.2007", 0.381),
    ("0.2518", 0.265),
    ("0.3102", 0.155),
]

print("为每个 vol_sus 值拟合最佳 decay_power:")
print("=" * 80)

for case_val, peak_time in cases:
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case_val}.wav"
    
    ref_rate, ref_data = wavfile.read(ref_file)
    
    if ref_data.dtype == np.int16:
        ref_data = ref_data.astype(np.float32) / 32768.0
    
    window_size = 128
    ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                        for i in range(0, len(ref_data), window_size//8)])
    
    env_time = np.arange(len(ref_env)) * (window_size/8) / ref_rate
    
    # 找峰值
    peak_idx = np.argmax(ref_env)
    actual_peak_time = env_time[peak_idx]
    peak_val = ref_env[peak_idx]
    
    # 提取 decay 段的数据点 (从峰值到 2 秒)
    decay_mask = (env_time >= actual_peak_time) & (env_time <= actual_peak_time + 1.5)
    decay_time_vals = env_time[decay_mask] - actual_peak_time
    decay_env_vals = ref_env[decay_mask] / peak_val  # 归一化
    
    # 拟合 decay_power
    # 模型: y = (1 - t/T)^p, where T=1.3 (decay_time)
    decay_T = 1.3
    
    def loss(p):
        if p < 0.5 or p > 10.0:
            return 1e10
        predicted = np.array([(1.0 - min(t/decay_T, 1.0))**p for t in decay_time_vals])
        return np.sum((predicted - decay_env_vals)**2)
    
    result = minimize_scalar(loss, bounds=(0.5, 10.0), method='bounded')
    best_power = result.x
    
    # 计算关键时间点的值
    test_times = [0.2, 0.4, 0.6, 0.8]
    ref_vals = []
    fitted_vals = []
    
    for t in test_times:
        idx = np.argmin(np.abs(env_time - (actual_peak_time + t)))
        ref_vals.append(ref_env[idx] / peak_val)
        
        if t < decay_T:
            fitted_vals.append((1.0 - t/decay_T)**best_power)
        else:
            fitted_vals.append(0.0)
    
    print(f"vol_sus={case_val}: best_power={best_power:.2f}")
    for i, t in enumerate(test_times):
        print(f"  +{t}s: ref={ref_vals[i]*100:.1f}%, fitted={fitted_vals[i]*100:.1f}%")
