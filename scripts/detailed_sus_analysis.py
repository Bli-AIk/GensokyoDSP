#!/usr/bin/env python3
"""详细分析 vol_sus 参数的包络"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# 读取参考文件和输出文件
ref_file = "tests/fixtures/vol_sus_tests/vol_sus_0.3102.wav"
out_file = "tests/output/test_vol_sus_0.3102.wav"

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

# 创建包络 (使用较小的窗口以获得更精细的细节)
window_size = 256
ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                    for i in range(0, len(ref_data), window_size//4)])
out_env = np.array([np.sqrt(np.mean(out_data[max(0,i-window_size//2):min(len(out_data),i+window_size//2)]**2)) 
                    for i in range(0, len(out_data), window_size//4)])

env_time = np.arange(len(ref_env)) * (window_size/4) / ref_rate

print(f"vol_sus = 0.3102 的详细分析")
print(f"总时长: {len(ref_data)/ref_rate:.3f} 秒")
print(f"包络点数: {len(ref_env)}")

# 找到包络的关键点
ref_max = np.max(ref_env)
out_max = np.max(out_env)
ref_max_idx = np.argmax(ref_env)
out_max_idx = np.argmax(out_env)

print(f"\n参考音频包络:")
print(f"  最大值: {ref_max:.6f} at {env_time[ref_max_idx]:.3f}s")

print(f"\n输出音频包络:")
print(f"  最大值: {out_max:.6f} at {env_time[out_max_idx]:.3f}s")

# 找到衰减到 sustain 水平的时间点
# sustain 水平应该是 vol_sus 参数控制的
threshold = ref_max * 0.1

# 找到 sustain 段 (在最大值之后的稳定段)
sus_start_idx = ref_max_idx + 100  # 跳过衰减段初期
sus_end_idx = min(sus_start_idx + 500, len(ref_env) - 1)

if sus_start_idx < len(ref_env):
    ref_sus_level = np.mean(ref_env[sus_start_idx:sus_end_idx])
    out_sus_level = np.mean(out_env[sus_start_idx:sus_end_idx])
    
    print(f"\n推测的 sustain 水平:")
    print(f"  参考: {ref_sus_level:.6f}")
    print(f"  输出: {out_sus_level:.6f}")
    print(f"  差异: {abs(ref_sus_level - out_sus_level):.6f}")
    print(f"  比例: {out_sus_level/ref_sus_level if ref_sus_level > 0 else 0:.4f}")

# 分析整个包络的形状相似度
# 使用对数空间来强调低电平的差异
ref_env_log = np.log10(ref_env + 1e-10)
out_env_log = np.log10(out_env + 1e-10)

corr = np.corrcoef(ref_env_log, out_env_log)[0, 1]
print(f"\n包络形状相关性: {corr:.6f}")

# 可视化
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 包络对比 (线性)
axes[0].plot(env_time, ref_env, label='Reference', linewidth=2)
axes[0].plot(env_time, out_env, label='Output', linewidth=2, alpha=0.7)
axes[0].axhline(y=ref_sus_level if sus_start_idx < len(ref_env) else 0, 
                color='r', linestyle='--', alpha=0.5, label='Ref Sustain Level')
axes[0].axhline(y=out_sus_level if sus_start_idx < len(ref_env) else 0, 
                color='b', linestyle='--', alpha=0.5, label='Out Sustain Level')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('RMS Amplitude')
axes[0].set_title('Envelope Comparison (Linear)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 包络对比 (对数)
axes[1].semilogy(env_time, ref_env + 1e-10, label='Reference', linewidth=2)
axes[1].semilogy(env_time, out_env + 1e-10, label='Output', linewidth=2, alpha=0.7)
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('RMS Amplitude (log)')
axes[1].set_title('Envelope Comparison (Logarithmic)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 包络差异百分比
env_diff_pct = np.zeros_like(ref_env)
for i in range(len(ref_env)):
    if ref_env[i] > 1e-6:
        env_diff_pct[i] = abs(out_env[i] - ref_env[i]) / ref_env[i] * 100.0

axes[2].plot(env_time, env_diff_pct, color='purple', linewidth=2)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Difference (%)')
axes[2].set_title('Envelope Difference (% of Reference)')
axes[2].axhline(y=5, color='r', linestyle='--', label='5% threshold')
axes[2].axhline(y=10, color='orange', linestyle='--', label='10% threshold')
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim([0, 50])

plt.tight_layout()
plt.savefig('vol_sus_3102_detailed.png', dpi=150)
print(f"\n详细图表已保存到 vol_sus_3102_detailed.png")

# 打印前几秒的详细数据
print(f"\n前2秒的包络数据对比 (每0.1秒):")
for t in np.arange(0, 2.0, 0.1):
    idx = int(t * ref_rate / (window_size/4))
    if idx < len(ref_env):
        print(f"  {t:.1f}s: ref={ref_env[idx]:.6f}, out={out_env[idx]:.6f}, diff={abs(ref_env[idx]-out_env[idx]):.6f}")
