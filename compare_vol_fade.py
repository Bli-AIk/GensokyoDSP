#!/usr/bin/env python3
"""对比生成和参考的vol_fade音频"""
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import sys

def analyze_file(filepath):
    """分析音频文件"""
    sr, data = wavfile.read(filepath)
    
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    else:
        data = data.astype(np.float64)
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 计算RMS包络
    chunk_size = int(sr * 0.01)  # 10ms
    times = []
    rms_values = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) == 0:
            break
        rms = np.sqrt(np.mean(chunk**2))
        rms_values.append(rms)
        times.append(i / sr)
    
    return np.array(times), np.array(rms_values)

def main():
    if len(sys.argv) < 2:
        vol_fade_val = "1.0"
    else:
        vol_fade_val = sys.argv[1]
    
    ref_file = f"tests/fixtures/vol_fade_tests/vol_fade_{vol_fade_val}.wav"
    gen_file = f"tests/output/test_vol_fade_{vol_fade_val}.wav"
    
    print(f"对比 vol_fade={vol_fade_val}")
    
    try:
        ref_times, ref_rms = analyze_file(ref_file)
        gen_times, gen_rms = analyze_file(gen_file)
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # 绘制对比图
    plt.figure(figsize=(15, 8))
    
    # 全部时长
    plt.subplot(2, 1, 1)
    plt.plot(ref_times, ref_rms, 'b-', label='参考', alpha=0.7, linewidth=2)
    plt.plot(gen_times, gen_rms, 'r--', label='生成', alpha=0.7, linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('RMS')
    plt.title(f'Vol Fade {vol_fade_val} - Full Duration')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 前3秒
    plt.subplot(2, 1, 2)
    mask_ref = ref_times <= 3.0
    mask_gen = gen_times <= 3.0
    plt.plot(ref_times[mask_ref], ref_rms[mask_ref], 'b-', label='参考', alpha=0.7, linewidth=2)
    plt.plot(gen_times[mask_gen], gen_rms[mask_gen], 'r--', label='生成', alpha=0.7, linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('RMS')
    plt.title(f'Vol Fade {vol_fade_val} - First 3 seconds')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    filename = f'vol_fade_{vol_fade_val}_comparison.png'
    plt.savefig(filename, dpi=150)
    print(f"图表已保存到 {filename}")
    
    # 打印统计信息
    print(f"\n参考音频:")
    print(f"  峰值RMS: {np.max(ref_rms):.4f} at {ref_times[np.argmax(ref_rms)]:.3f}s")
    print(f"  时长: {ref_times[-1]:.3f}s")
    
    print(f"\n生成音频:")
    print(f"  峰值RMS: {np.max(gen_rms):.4f} at {gen_times[np.argmax(gen_rms)]:.3f}s")
    print(f"  时长: {gen_times[-1]:.3f}s")
    
    # 找到淡出点
    ref_peak_idx = np.argmax(ref_rms)
    gen_peak_idx = np.argmax(gen_rms)
    
    ref_fade_start = None
    for i in range(ref_peak_idx, len(ref_rms)):
        if ref_rms[i] < np.max(ref_rms) * 0.9:
            ref_fade_start = ref_times[i]
            break
    
    gen_fade_start = None
    for i in range(gen_peak_idx, len(gen_rms)):
        if gen_rms[i] < np.max(gen_rms) * 0.9:
            gen_fade_start = gen_times[i]
            break
    
    if ref_fade_start:
        print(f"\n参考淡出开始: ~{ref_fade_start:.3f}s")
    if gen_fade_start:
        print(f"生成淡出开始: ~{gen_fade_start:.3f}s")

if __name__ == "__main__":
    main()
