#!/usr/bin/env python3
"""分析a_color参数对噪声频谱的影响"""
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

def analyze_color(filepath, color_value):
    """分析单个color音频文件"""
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
    
    # 取中间1秒的数据进行频谱分析
    mid_start = len(data) // 2
    mid_end = mid_start + sr
    segment = data[mid_start:mid_end]
    
    # RMS
    rms = np.sqrt(np.mean(segment**2))
    
    # FFT
    fft_data = np.fft.rfft(segment)
    freqs = np.fft.rfftfreq(len(segment), 1/sr)
    magnitude = np.abs(fft_data)
    power = magnitude ** 2
    
    # 分析频带能量
    bands = {
        '0-100Hz': (0, 100),
        '100-500Hz': (100, 500),
        '500-1kHz': (500, 1000),
        '1k-2kHz': (1000, 2000),
        '2k-5kHz': (2000, 5000),
        '5k-10kHz': (5000, 10000),
        '10k-20kHz': (10000, 20000),
    }
    
    total_power = np.sum(power)
    band_powers = {}
    
    for band_name, (f_low, f_high) in bands.items():
        mask = (freqs >= f_low) & (freqs < f_high)
        band_power = np.sum(power[mask])
        band_percent = 100 * band_power / total_power if total_power > 0 else 0
        band_powers[band_name] = band_percent
    
    # 计算频谱斜率（log-log）
    # 选择200Hz到10kHz范围
    freq_range_mask = (freqs >= 200) & (freqs <= 10000)
    log_freqs = np.log10(freqs[freq_range_mask])
    log_power = np.log10(power[freq_range_mask] + 1e-10)
    
    # 线性拟合
    coeffs = np.polyfit(log_freqs, log_power, 1)
    slope = coeffs[0]
    
    return {
        'color': color_value,
        'rms': rms,
        'slope': slope,  # 负斜率表示低频能量高（棕色），正斜率表示高频能量高
        'band_powers': band_powers,
        'freqs': freqs,
        'power': power
    }

def main():
    color_values = [0.0, 0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 0.3540,
                    0.4051, 0.4536, 0.4958, 0.5506, 0.6055, 0.6519, 0.7025,
                    0.7489, 0.8080, 0.8502, 0.9051, 0.9515, 1.0]
    
    results = []
    for val in color_values:
        filepath = f"tests/fixtures/a_color_tests/a_color_{val}.wav"
        result = analyze_color(filepath, val)
        if result:
            results.append(result)
    
    if not results:
        print("没有成功分析任何文件")
        return
    
    # 打印统计信息
    print("=== a_color参数分析 ===\n")
    print(f"{'a_color':>8} | {'RMS':>8} | {'斜率':>8} | {'低频%':>8} | {'高频%':>8}")
    print("-" * 60)
    
    for res in results:
        low_freq = res['band_powers']['0-100Hz'] + res['band_powers']['100-500Hz']
        high_freq = res['band_powers']['5k-10kHz'] + res['band_powers']['10k-20kHz']
        print(f"{res['color']:8.4f} | {res['rms']:8.6f} | {res['slope']:8.3f} | "
              f"{low_freq:8.2f} | {high_freq:8.2f}")
    
    # 绘制频谱对比
    plt.figure(figsize=(15, 10))
    
    # 选择几个代表性的值
    selected_indices = [0, 5, 10, 15, 20]  # 0.0, 0.2518, 0.4958, 0.7489, 1.0
    colors_plot = ['darkblue', 'blue', 'green', 'orange', 'red']
    
    plt.subplot(2, 1, 1)
    for idx, color_plot in zip(selected_indices, colors_plot):
        if idx < len(results):
            res = results[idx]
            # 只绘制到15kHz
            mask = res['freqs'] < 15000
            plt.plot(res['freqs'][mask], 10*np.log10(res['power'][mask] + 1e-10), 
                     label=f"a_color={res['color']:.4f}", alpha=0.7, color=color_plot, linewidth=2)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (dB)')
    plt.title('Frequency Spectrum vs a_color (0-15kHz)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xscale('log')
    
    # 绘制斜率变化曲线
    plt.subplot(2, 1, 2)
    color_vals = [r['color'] for r in results]
    slopes = [r['slope'] for r in results]
    rms_vals = [r['rms'] for r in results]
    
    plt.plot(color_vals, slopes, 'b-o', label='Spectral Slope', alpha=0.7, markersize=4)
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    plt.xlabel('a_color')
    plt.ylabel('Spectral Slope (log-log)')
    plt.title('Spectral Slope vs a_color\n(负值=棕色噪声, 0=粉红噪声, 正值=白噪声)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('a_color_analysis.png', dpi=150)
    print("\n图表已保存到 a_color_analysis.png")
    
    # 打印详细频带分布（选几个关键值）
    print("\n=== 详细频带能量分布 ===")
    for idx in [0, 10, 20]:
        if idx < len(results):
            res = results[idx]
            print(f"\na_color = {res['color']:.4f}:")
            for band, percent in res['band_powers'].items():
                print(f"  {band:12s}: {percent:6.2f}%")

if __name__ == "__main__":
    main()
