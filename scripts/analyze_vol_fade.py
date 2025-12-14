#!/usr/bin/env python3
"""分析vol_fade参数对音频包络的影响"""
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import sys

def analyze_vol_fade(filepath, vol_fade_value):
    """分析单个vol_fade音频文件"""
    try:
        sr, data = wavfile.read(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    # 转换为浮点数
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    else:
        data = data.astype(np.float64)
    
    # 如果是立体声，取第一个声道
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 计算RMS包络
    chunk_size = int(sr * 0.01)  # 10ms chunks
    times = []
    rms_values = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) == 0:
            break
        rms = np.sqrt(np.mean(chunk**2))
        rms_values.append(rms)
        times.append(i / sr)
    
    return {
        'times': np.array(times),
        'rms': np.array(rms_values),
        'vol_fade': vol_fade_value,
        'sr': sr,
        'duration': len(data) / sr
    }

def main():
    # vol_fade测试文件列表
    vol_fade_values = [
        "0.0547", "0.1058", "0.1496", "0.2007", "0.2518", "0.3102", "0.3540",
        "0.4051", "0.4536", "0.4958", "0.5506", "0.6055", "0.6519", "0.7025",
        "0.7489", "0.8080", "0.8502", "0.9051", "0.9515", "1.0"
    ]
    
    results = []
    for val in vol_fade_values:
        filepath = f"tests/fixtures/vol_fade_tests/vol_fade_{val}.wav"
        result = analyze_vol_fade(filepath, float(val))
        if result:
            results.append(result)
            print(f"vol_fade={val}: duration={result['duration']:.3f}s, peak_rms={np.max(result['rms']):.4f}")
    
    if not results:
        print("没有成功分析任何文件")
        return
    
    # 绘制所有包络
    plt.figure(figsize=(15, 10))
    
    # 绘制前5秒
    plt.subplot(2, 1, 1)
    for res in results:
        mask = res['times'] <= 5.0
        plt.plot(res['times'][mask], res['rms'][mask], label=f"vol_fade={res['vol_fade']}", alpha=0.7)
    plt.xlabel('Time (s)')
    plt.ylabel('RMS')
    plt.title('Vol Fade Envelopes (0-5s)')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # 绘制全部时长
    plt.subplot(2, 1, 2)
    for res in results:
        plt.plot(res['times'], res['rms'], label=f"vol_fade={res['vol_fade']}", alpha=0.7)
    plt.xlabel('Time (s)')
    plt.ylabel('RMS')
    plt.title('Vol Fade Envelopes (Full)')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('vol_fade_analysis.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存到 vol_fade_analysis.png")
    
    # 打印详细分析
    print("\n=== 详细分析 ===")
    for res in results:
        times = res['times']
        rms = res['rms']
        peak_rms = np.max(rms)
        peak_time = times[np.argmax(rms)]
        
        # 找到淡出开始点 (峰值后RMS下降到峰值90%的时刻)
        peak_idx = np.argmax(rms)
        fade_start = None
        for i in range(peak_idx, len(rms)):
            if rms[i] < peak_rms * 0.9:
                fade_start = times[i]
                break
        
        # 找到10%的时刻
        ten_percent_time = None
        for i in range(peak_idx, len(rms)):
            if rms[i] < peak_rms * 0.1:
                ten_percent_time = times[i]
                break
        
        print(f"\nvol_fade={res['vol_fade']:.4f}:")
        print(f"  峰值RMS: {peak_rms:.4f} at {peak_time:.3f}s")
        if fade_start:
            print(f"  淡出开始: ~{fade_start:.3f}s (90% of peak)")
        if ten_percent_time:
            print(f"  降至10%: ~{ten_percent_time:.3f}s")
            if fade_start:
                print(f"  淡出时长: ~{ten_percent_time - fade_start:.3f}s")

if __name__ == "__main__":
    main()
