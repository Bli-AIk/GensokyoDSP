#!/usr/bin/env python3
"""分析 vol_sus_0.3102 测试失败的原因"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sys

# 读取参考文件和输出文件
ref_file = "tests/fixtures/vol_sus_tests/vol_sus_0.3102.wav"
out_file = "tests/output/test_vol_sus_0.3102.wav"

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
    
    # 计算差异
    diff = ref_data - out_data
    
    # 详细分析
    print(f"采样率: ref={ref_rate}, out={out_rate}")
    print(f"样本数: ref={len(ref_data)}, out={len(out_data)}")
    print(f"\n参考音频统计:")
    print(f"  RMS: {np.sqrt(np.mean(ref_data**2)):.6f}")
    print(f"  Max: {np.max(np.abs(ref_data)):.6f}")
    print(f"  Mean: {np.mean(ref_data):.6f}")
    
    print(f"\n输出音频统计:")
    print(f"  RMS: {np.sqrt(np.mean(out_data**2)):.6f}")
    print(f"  Max: {np.max(np.abs(out_data)):.6f}")
    print(f"  Mean: {np.mean(out_data):.6f}")
    
    print(f"\n差异统计:")
    print(f"  RMS差异: {np.sqrt(np.mean(diff**2)):.6f}")
    print(f"  Max差异: {np.max(np.abs(diff)):.6f}")
    
    # 计算相似度
    ref_rms = np.sqrt(np.mean(ref_data**2))
    diff_rms = np.sqrt(np.mean(diff**2))
    similarity = (1.0 - diff_rms / ref_rms) * 100.0
    print(f"  相似度: {similarity:.2f}%")
    
    # 分段分析
    segment_size = len(ref_data) // 10
    print(f"\n分段分析 (每段 {segment_size} 样本):")
    for i in range(10):
        start = i * segment_size
        end = start + segment_size
        if end > len(ref_data):
            end = len(ref_data)
        
        ref_seg = ref_data[start:end]
        out_seg = out_data[start:end]
        diff_seg = ref_seg - out_seg
        
        ref_seg_rms = np.sqrt(np.mean(ref_seg**2))
        diff_seg_rms = np.sqrt(np.mean(diff_seg**2))
        
        if ref_seg_rms > 0:
            seg_similarity = (1.0 - diff_seg_rms / ref_seg_rms) * 100.0
        else:
            seg_similarity = 100.0
            
        print(f"  段 {i}: RMS_ref={ref_seg_rms:.6f}, RMS_diff={diff_seg_rms:.6f}, 相似度={seg_similarity:.2f}%")
    
    # 绘制波形对比
    fig, axes = plt.subplots(4, 1, figsize=(14, 10))
    
    # 完整波形
    time = np.arange(len(ref_data)) / ref_rate
    axes[0].plot(time, ref_data, label='Reference', alpha=0.7, linewidth=0.5)
    axes[0].plot(time, out_data, label='Output', alpha=0.7, linewidth=0.5)
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Complete Waveform Comparison')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 差异
    axes[1].plot(time, diff, color='red', linewidth=0.5)
    axes[1].set_xlabel('Time (s)')
    axes[1].set_ylabel('Difference')
    axes[1].set_title('Difference (Reference - Output)')
    axes[1].grid(True, alpha=0.3)
    
    # 包络对比 (RMS)
    window_size = 512
    ref_env = np.array([np.sqrt(np.mean(ref_data[i:i+window_size]**2)) 
                        for i in range(0, len(ref_data)-window_size, window_size)])
    out_env = np.array([np.sqrt(np.mean(out_data[i:i+window_size]**2)) 
                        for i in range(0, len(out_data)-window_size, window_size)])
    env_time = np.arange(len(ref_env)) * window_size / ref_rate
    
    axes[2].plot(env_time, ref_env, label='Reference Envelope', linewidth=2)
    axes[2].plot(env_time, out_env, label='Output Envelope', linewidth=2, alpha=0.7)
    axes[2].set_xlabel('Time (s)')
    axes[2].set_ylabel('RMS Amplitude')
    axes[2].set_title('Envelope Comparison (RMS with window=512)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    # 包络差异百分比
    env_diff_pct = np.zeros_like(ref_env)
    for i in range(len(ref_env)):
        if ref_env[i] > 1e-6:
            env_diff_pct[i] = abs(out_env[i] - ref_env[i]) / ref_env[i] * 100.0
        else:
            env_diff_pct[i] = 0.0
    
    axes[3].plot(env_time, env_diff_pct, color='purple', linewidth=2)
    axes[3].set_xlabel('Time (s)')
    axes[3].set_ylabel('Difference (%)')
    axes[3].set_title('Envelope Difference (% of Reference)')
    axes[3].axhline(y=5, color='r', linestyle='--', label='5% threshold')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('vol_sus_3102_analysis.png', dpi=150)
    print(f"\n图表已保存到 vol_sus_3102_analysis.png")
    
except FileNotFoundError as e:
    print(f"错误: 文件未找到 - {e}")
    sys.exit(1)
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
