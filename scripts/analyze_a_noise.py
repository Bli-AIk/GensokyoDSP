#!/usr/bin/env python3
"""分析a_noise参数对音频的影响"""
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy import signal

def analyze_noise(filepath, noise_value):
    """分析单个noise音频文件"""
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
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 计算RMS
    rms = np.sqrt(np.mean(data**2))
    peak = np.max(np.abs(data))
    
    # 计算频谱
    # 取中间1秒的数据进行频谱分析
    mid_start = len(data) // 2
    mid_end = mid_start + sr
    segment = data[mid_start:mid_end]
    
    # FFT
    fft_data = np.fft.rfft(segment)
    freqs = np.fft.rfftfreq(len(segment), 1/sr)
    magnitude = np.abs(fft_data)
    
    # 计算频谱的几个统计量
    # 基频能量（假设是523Hz附近，C5音）
    fund_freq = 523.25
    fund_idx = np.argmin(np.abs(freqs - fund_freq))
    fund_energy = magnitude[fund_idx]
    
    # 低频能量（0-1kHz）
    low_mask = freqs < 1000
    low_energy = np.sum(magnitude[low_mask]**2)
    
    # 高频能量（1kHz-20kHz）
    high_mask = (freqs >= 1000) & (freqs < 20000)
    high_energy = np.sum(magnitude[high_mask]**2)
    
    # 总能量
    total_energy = np.sum(magnitude**2)
    
    return {
        'noise': noise_value,
        'rms': rms,
        'peak': peak,
        'fund_energy': fund_energy,
        'low_energy': low_energy,
        'high_energy': high_energy,
        'total_energy': total_energy,
        'high_to_total_ratio': high_energy / total_energy if total_energy > 0 else 0,
        'freqs': freqs,
        'magnitude': magnitude
    }

def main():
    noise_values = [
        0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 0.3540,
        0.4051, 0.4536, 0.4958, 0.5506, 0.6055, 0.6519, 0.7025,
        0.7489, 0.8080, 0.8502, 0.9051, 0.9515, 1.0
    ]
    
    results = []
    for val in noise_values:
        filepath = f"tests/fixtures/a_noise_tests/a_noise_{val}.wav"
        result = analyze_noise(filepath, val)
        if result:
            results.append(result)
    
    if not results:
        print("没有成功分析任何文件")
        return
    
    # 打印统计信息
    print("=== a_noise参数分析 ===\n")
    print(f"{'a_noise':>8} | {'RMS':>8} | {'Peak':>8} | {'高频比':>8} | {'基频能量':>10}")
    print("-" * 60)
    
    for res in results:
        print(f"{res['noise']:8.4f} | {res['rms']:8.6f} | {res['peak']:8.6f} | "
              f"{res['high_to_total_ratio']:8.4f} | {res['fund_energy']:10.2f}")
    
    # 绘制频谱对比（选择几个代表性的值）
    plt.figure(figsize=(15, 10))
    
    # 选择0.0547, 0.3102, 0.6055, 1.0
    selected = [0, 5, 11, 19]
    colors = ['blue', 'green', 'orange', 'red']
    
    plt.subplot(2, 1, 1)
    for idx, color in zip(selected, colors):
        res = results[idx]
        # 只绘制到10kHz
        mask = res['freqs'] < 10000
        plt.plot(res['freqs'][mask], 20*np.log10(res['magnitude'][mask] + 1e-10), 
                 label=f"a_noise={res['noise']:.4f}", alpha=0.7, color=color)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Frequency Spectrum (0-10kHz)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 绘制RMS和高频比的变化曲线
    plt.subplot(2, 1, 2)
    noise_vals = [r['noise'] for r in results]
    rms_vals = [r['rms'] for r in results]
    high_ratios = [r['high_to_total_ratio'] for r in results]
    
    plt.plot(noise_vals, rms_vals, 'b-o', label='RMS', alpha=0.7)
    plt.plot(noise_vals, high_ratios, 'r-o', label='High Freq Ratio', alpha=0.7)
    plt.xlabel('a_noise')
    plt.ylabel('Value')
    plt.title('RMS and High Frequency Ratio vs a_noise')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('a_noise_analysis.png', dpi=150)
    print("\n图表已保存到 a_noise_analysis.png")

if __name__ == "__main__":
    main()
