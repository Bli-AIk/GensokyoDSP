#!/usr/bin/env python3
"""分析 attack 曲线的形状"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

cases = {
    "0.1058": (0.317, False),  # 峰值时间, 是否通过
    "0.1496": (0.489, False),
    "0.2007": (0.381, False),
}

fig, axes = plt.subplots(len(cases), 2, figsize=(14, 4*len(cases)))

for idx, (case, (peak_time, passed)) in enumerate(cases.items()):
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    out_file = f"tests/output/test_vol_sus_{case}.wav"
    
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
    
    # 归一化包络 (到峰值)
    ref_max = np.max(ref_env)
    out_max = np.max(out_env)
    ref_env_norm = ref_env / ref_max
    out_env_norm = out_env / out_max
    
    # 找到峰值索引
    ref_max_idx = np.argmax(ref_env)
    out_max_idx = np.argmax(out_env)
    
    # 绘制归一化包络 (只看 attack 和衰减的前半部分)
    plot_duration = peak_time * 2.5
    plot_mask = env_time < plot_duration
    
    axes[idx, 0].plot(env_time[plot_mask], ref_env_norm[plot_mask], 
                      label='Reference (normalized)', linewidth=2)
    axes[idx, 0].plot(env_time[plot_mask], out_env_norm[plot_mask], 
                      label='Output (normalized)', linewidth=2, alpha=0.7)
    axes[idx, 0].axvline(x=peak_time, color='r', linestyle='--', alpha=0.5, label='Expected peak')
    axes[idx, 0].set_xlabel('Time (s)')
    axes[idx, 0].set_ylabel('Normalized Amplitude')
    axes[idx, 0].set_title(f'vol_sus_{case} - Normalized Envelope')
    axes[idx, 0].legend()
    axes[idx, 0].grid(True, alpha=0.3)
    
    # 绘制未归一化的包络比较
    axes[idx, 1].plot(env_time[plot_mask], ref_env[plot_mask], 
                      label='Reference', linewidth=2)
    axes[idx, 1].plot(env_time[plot_mask], out_env[plot_mask], 
                      label='Output', linewidth=2, alpha=0.7)
    axes[idx, 1].axvline(x=peak_time, color='r', linestyle='--', alpha=0.5, label='Expected peak')
    axes[idx, 1].set_xlabel('Time (s)')
    axes[idx, 1].set_ylabel('RMS Amplitude')
    axes[idx, 1].set_title(f'vol_sus_{case} - Actual Envelope')
    axes[idx, 1].legend()
    axes[idx, 1].grid(True, alpha=0.3)
    
    # 计算归一化包络的相似度
    min_len_env = min(len(ref_env_norm), len(out_env_norm))
    corr = np.corrcoef(ref_env_norm[:min_len_env], out_env_norm[:min_len_env])[0, 1]
    
    print(f"\nvol_sus_{case}:")
    print(f"  归一化包络相关性: {corr:.6f}")
    print(f"  峰值幅度比: {out_max/ref_max:.4f}")

plt.tight_layout()
plt.savefig('attack_curve_analysis.png', dpi=150)
print(f"\n图表已保存到 attack_curve_analysis.png")
