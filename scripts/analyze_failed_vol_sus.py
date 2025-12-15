#!/usr/bin/env python3
"""分析失败的 vol_sus 测试"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sys

cases = ["0.1058", "0.1496", "0.2007"]

fig, axes = plt.subplots(len(cases), 3, figsize=(18, 4*len(cases)))

for idx, case in enumerate(cases):
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    out_file = f"tests/output/test_vol_sus_{case}.wav"
    
    try:
        ref_rate, ref_data = wavfile.read(ref_file)
        out_rate, out_data = wavfile.read(out_file)
        
        # 转换为浮点数
        if ref_data.dtype == np.int16:
            ref_data = ref_data.astype(np.float32) / 32768.0
        if out_data.dtype == np.int16:
            out_data = out_data.astype(np.float32) / 32768.0
        
        # 确保长度相同
        min_len = min(len(ref_data), len(out_data))
        ref_data = ref_data[:min_len]
        out_data = out_data[:min_len]
        
        # 创建包络
        window_size = 256
        ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                            for i in range(0, len(ref_data), window_size//4)])
        out_env = np.array([np.sqrt(np.mean(out_data[max(0,i-window_size//2):min(len(out_data),i+window_size//2)]**2)) 
                            for i in range(0, len(out_data), window_size//4)])
        
        env_time = np.arange(len(ref_env)) * (window_size/4) / ref_rate
        
        # 找到峰值
        ref_max = np.max(ref_env)
        out_max = np.max(out_env)
        ref_max_idx = np.argmax(ref_env)
        out_max_idx = np.argmax(out_env)
        
        print(f"\nvol_sus_{case}:")
        print(f"  参考峰值: {ref_max:.6f} at {env_time[ref_max_idx]:.3f}s")
        print(f"  输出峰值: {out_max:.6f} at {env_time[out_max_idx]:.3f}s")
        print(f"  峰值时间差: {abs(env_time[ref_max_idx] - env_time[out_max_idx]):.3f}s")
        print(f"  峰值幅度比: {out_max/ref_max:.4f}")
        
        # 包络对比 (线性)
        axes[idx, 0].plot(env_time, ref_env, label='Reference', linewidth=2)
        axes[idx, 0].plot(env_time, out_env, label='Output', linewidth=2, alpha=0.7)
        axes[idx, 0].set_xlabel('Time (s)')
        axes[idx, 0].set_ylabel('RMS Amplitude')
        axes[idx, 0].set_title(f'vol_sus_{case} - Envelope (Linear)')
        axes[idx, 0].legend()
        axes[idx, 0].grid(True, alpha=0.3)
        axes[idx, 0].set_xlim([0, 2])
        
        # 包络对比 (对数)
        axes[idx, 1].semilogy(env_time, ref_env + 1e-10, label='Reference', linewidth=2)
        axes[idx, 1].semilogy(env_time, out_env + 1e-10, label='Output', linewidth=2, alpha=0.7)
        axes[idx, 1].set_xlabel('Time (s)')
        axes[idx, 1].set_ylabel('RMS Amplitude (log)')
        axes[idx, 1].set_title(f'vol_sus_{case} - Envelope (Log)')
        axes[idx, 1].legend()
        axes[idx, 1].grid(True, alpha=0.3)
        axes[idx, 1].set_xlim([0, 2])
        
        # 包络差异百分比
        env_diff_pct = np.zeros_like(ref_env)
        for i in range(len(ref_env)):
            if ref_env[i] > 1e-6:
                env_diff_pct[i] = abs(out_env[i] - ref_env[i]) / ref_env[i] * 100.0
        
        axes[idx, 2].plot(env_time, env_diff_pct, color='purple', linewidth=2)
        axes[idx, 2].set_xlabel('Time (s)')
        axes[idx, 2].set_ylabel('Difference (%)')
        axes[idx, 2].set_title(f'vol_sus_{case} - Envelope Diff %')
        axes[idx, 2].axhline(y=5, color='r', linestyle='--', label='5% threshold')
        axes[idx, 2].legend()
        axes[idx, 2].grid(True, alpha=0.3)
        axes[idx, 2].set_xlim([0, 2])
        axes[idx, 2].set_ylim([0, 50])
        
    except Exception as e:
        print(f"Error processing {case}: {e}")

plt.tight_layout()
plt.savefig('failed_vol_sus_analysis.png', dpi=150)
print(f"\n图表已保存到 failed_vol_sus_analysis.png")
