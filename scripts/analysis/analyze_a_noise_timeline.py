#!/usr/bin/env python3
"""
详细分析a_noise失败测试的时间域特征
"""

import numpy as np
import wave
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(str(filename), 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        frames = wav.readframes(n_frames)
        
        if sample_width == 2:
            data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:
            data = np.frombuffer(frames, dtype=np.int32)
        else:
            raise ValueError(f"不支持的采样位深: {sample_width}")
        
        data = data.astype(np.float64) / (2**(sample_width * 8 - 1))
        
        if n_channels == 2:
            data = data[::2]
        
        return data, framerate

def analyze_time_segments(a_noise_value):
    """分析时间段RMS"""
    base_path = Path("/workspaces/GensokyoDSP")
    
    ref_file = base_path / "tests" / "fixtures" / "a_noise_tests" / f"a_noise_{a_noise_value}.wav"
    test_file = base_path / "tests" / "output" / f"test_a_noise_{a_noise_value}.wav"
    
    if not ref_file.exists() or not test_file.exists():
        return None
    
    ref_data, ref_sr = read_wav(ref_file)
    test_data, test_sr = read_wav(test_file)
    
    # 计算RMS随时间变化
    segment_dur = 0.05  # 50ms segments
    segment_samples = int(segment_dur * ref_sr)
    
    min_len = min(len(ref_data), len(test_data))
    n_segments = min_len // segment_samples
    
    times = []
    ref_rms_list = []
    test_rms_list = []
    
    for i in range(n_segments):
        start = i * segment_samples
        end = start + segment_samples
        
        ref_seg = ref_data[start:end]
        test_seg = test_data[start:end]
        
        ref_rms = np.sqrt(np.mean(ref_seg**2))
        test_rms = np.sqrt(np.mean(test_seg**2))
        
        times.append(i * segment_dur)
        ref_rms_list.append(ref_rms)
        test_rms_list.append(test_rms)
    
    return times, ref_rms_list, test_rms_list

def plot_comparison(a_noise_values):
    """绘制对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, value in enumerate(a_noise_values):
        result = analyze_time_segments(value)
        if result is None:
            continue
        
        times, ref_rms, test_rms = result
        
        ax = axes[idx]
        ax.plot(times, ref_rms, 'b-', label='参考', alpha=0.7)
        ax.plot(times, test_rms, 'r-', label='测试', alpha=0.7)
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('RMS')
        ax.set_title(f'a_noise={value}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 标注起音阶段差异
        if len(times) > 20:
            early_ref = np.mean(ref_rms[:20])
            early_test = np.mean(test_rms[:20])
            ax.text(0.5, 0.95, f'起音阶段: 参考={early_ref:.4f}, 测试={early_test:.4f}',
                   transform=ax.transAxes, va='top', fontsize=8,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    output_path = Path("/workspaces/GensokyoDSP/scripts/analysis/plots/a_noise_time_comparison.png")
    plt.savefig(output_path, dpi=150)
    print(f"图表已保存到: {output_path}")

def main():
    # 分析失败的测试
    failed_values = ['0.8502', '0.9051', '0.9515', '1.0']
    
    print("详细时间域分析:")
    print("=" * 80)
    
    for value in failed_values:
        result = analyze_time_segments(value)
        if result is None:
            continue
        
        times, ref_rms, test_rms = result
        
        print(f"\na_noise={value}:")
        print(f"  {'时间(s)':<10} {'参考RMS':<12} {'测试RMS':<12} {'比例':<10}")
        print("  " + "-" * 50)
        
        # 前1秒，每0.1秒
        for i in range(0, min(20, len(times)), 2):
            t = times[i]
            r_rms = ref_rms[i]
            t_rms = test_rms[i]
            ratio = t_rms / r_rms if r_rms > 0.0001 else 0
            print(f"  {t:<10.3f} {r_rms:<12.6f} {t_rms:<12.6f} {ratio:<10.3f}")
    
    # 绘制对比图
    plot_comparison(failed_values)

if __name__ == "__main__":
    main()
