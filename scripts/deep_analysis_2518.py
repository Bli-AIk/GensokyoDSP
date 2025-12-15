#!/usr/bin/env python3
"""深入分析 vol_sus_0.2518"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

case = "0.2518"
ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
out_file = f"tests/output/test_vol_sus_{case}.wav"

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

# 创建细粒度包络
window_size = 128
ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                    for i in range(0, len(ref_data), window_size//8)])
out_env = np.array([np.sqrt(np.mean(out_data[max(0,i-window_size//2):min(len(out_data),i+window_size//2)]**2)) 
                    for i in range(0, len(out_data), window_size//8)])

env_time = np.arange(len(ref_env)) * (window_size/8) / ref_rate

# 找到峰值
ref_max_idx = np.argmax(ref_env)
out_max_idx = np.argmax(out_env)
ref_max = ref_env[ref_max_idx]
out_max = out_env[out_max_idx]

print(f"vol_sus_{case} 详细分析:")
print(f"  参考峰值: {ref_max:.6f} at {env_time[ref_max_idx]:.3f}s")
print(f"  输出峰值: {out_max:.6f} at {env_time[out_max_idx]:.3f}s")
print(f"  峰值比: {out_max/ref_max:.4f}")

# 检查峰值前后的形状
before_peak = 50
after_peak = 150

ref_segment = ref_env[max(0, ref_max_idx-before_peak):min(len(ref_env), ref_max_idx+after_peak)]
out_segment = out_env[max(0, out_max_idx-before_peak):min(len(out_env), out_max_idx+after_peak)]

# 归一化到峰值
ref_segment_norm = ref_segment / ref_max
out_segment_norm = out_segment / out_max

# 计算相关性
min_seg_len = min(len(ref_segment_norm), len(out_segment_norm))
corr = np.corrcoef(ref_segment_norm[:min_seg_len], out_segment_norm[:min_seg_len])[0, 1]

print(f"  峰值附近形状相关性: {corr:.6f}")

# 绘图
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 完整包络
axes[0].plot(env_time, ref_env, label='Reference', linewidth=2)
axes[0].plot(env_time, out_env, label='Output', linewidth=2, alpha=0.7)
axes[0].axvline(x=env_time[ref_max_idx], color='r', linestyle='--', alpha=0.5, label='Ref peak')
axes[0].axvline(x=env_time[out_max_idx], color='b', linestyle='--', alpha=0.5, label='Out peak')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('RMS Amplitude')
axes[0].set_title(f'vol_sus_{case} - Full Envelope')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim([0, 2])

# 峰值附近的归一化形状
segment_time = np.arange(min_seg_len) * (window_size/8) / ref_rate
axes[1].plot(segment_time, ref_segment_norm[:min_seg_len], label='Reference (normalized)', linewidth=2)
axes[1].plot(segment_time, out_segment_norm[:min_seg_len], label='Output (normalized)', linewidth=2, alpha=0.7)
axes[1].set_xlabel('Time from segment start (s)')
axes[1].set_ylabel('Normalized Amplitude')
axes[1].set_title(f'Normalized Envelope Shape Around Peak (corr={corr:.4f})')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 差异
axes[2].plot(env_time, np.abs(ref_env - out_env), color='purple', linewidth=2)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Absolute Difference')
axes[2].set_title('Envelope Difference')
axes[2].grid(True, alpha=0.3)
axes[2].set_xlim([0, 2])

plt.tight_layout()
plt.savefig('vol_sus_2518_deep_analysis.png', dpi=150)
print(f"\n图表已保存到 vol_sus_2518_deep_analysis.png")

# 打印前 1 秒的详细数据
print(f"\n前 1 秒的包络数据对比 (每 0.05s):")
for t in np.arange(0, 1.0, 0.05):
    idx = int(t * ref_rate / (window_size/8))
    if idx < len(ref_env):
        diff_pct = abs(ref_env[idx] - out_env[idx]) / ref_env[idx] * 100 if ref_env[idx] > 0 else 0
        print(f"  {t:.2f}s: ref={ref_env[idx]:.6f}, out={out_env[idx]:.6f}, diff={diff_pct:.1f}%")
