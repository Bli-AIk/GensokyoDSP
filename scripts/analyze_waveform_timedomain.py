#!/usr/bin/env python3
"""分析时域波形差异"""

import wave
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def analyze_waveform_diff(ref_path, test_path, output_plot='/tmp/waveform_diff.png'):
    # 读取音频
    with wave.open(ref_path, 'r') as w:
        sr = w.getframerate()
        ref_data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        if w.getnchannels() == 2:
            ref_data = ref_data.reshape(-1, 2)[:, 0]
    
    with wave.open(test_path, 'r') as w:
        test_data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        if w.getnchannels() == 2:
            test_data = test_data.reshape(-1, 2)[:, 0]
    
    # 对齐长度
    min_len = min(len(ref_data), len(test_data))
    ref_data = ref_data[:min_len]
    test_data = test_data[:min_len]
    
    # 分析稳定段
    start = sr * 1
    end = sr * 2
    ref_seg = ref_data[start:end]
    test_seg = test_data[start:end]
    
    # 计算correlation
    correlation = np.corrcoef(ref_seg, test_seg)[0, 1]
    
    # 计算RMS
    ref_rms = np.sqrt(np.mean(ref_seg**2))
    test_rms = np.sqrt(np.mean(test_seg**2))
    
    # 计算差异
    diff = ref_seg - test_seg
    diff_rms = np.sqrt(np.mean(diff**2))
    
    print(f'时域分析:')
    print(f'  参考RMS: {ref_rms:.6f}')
    print(f'  测试RMS: {test_rms:.6f}')
    print(f'  RMS比率: {test_rms/ref_rms:.4f}')
    print(f'  差异RMS: {diff_rms:.6f}')
    print(f'  相关系数: {correlation:.6f}')
    print(f'  相似度: {(correlation+1)/2*100:.2f}%')
    
    # 绘制波形
    fig, axs = plt.subplots(3, 1, figsize=(15, 10))
    
    # 显示一个周期
    period = int(sr / 65.0)  # 65Hz的一个周期
    plot_start = start
    plot_end = plot_start + period * 3
    
    t = np.arange(period * 3) / sr * 1000  # 转换为ms
    
    axs[0].plot(t, ref_data[plot_start:plot_end], 'b-', label='Reference', linewidth=1)
    axs[0].plot(t, test_data[plot_start:plot_end], 'r--', label='Test', linewidth=1, alpha=0.7)
    axs[0].set_title('Waveform Comparison (3 periods)')
    axs[0].set_xlabel('Time (ms)')
    axs[0].set_ylabel('Amplitude')
    axs[0].legend()
    axs[0].grid(True, alpha=0.3)
    
    # 差异波形
    axs[1].plot(t, diff[plot_start-start:plot_end-start], 'g-', linewidth=1)
    axs[1].set_title('Difference Waveform')
    axs[1].set_xlabel('Time (ms)')
    axs[1].set_ylabel('Difference')
    axs[1].grid(True, alpha=0.3)
    
    # FFT比较
    fft_ref = np.abs(np.fft.rfft(ref_seg))
    fft_test = np.abs(np.fft.rfft(test_seg))
    freqs = np.fft.rfftfreq(len(ref_seg), 1/sr)
    
    axs[2].plot(freqs[:2000], fft_ref[:2000], 'b-', label='Reference', linewidth=1)
    axs[2].plot(freqs[:2000], fft_test[:2000], 'r--', label='Test', linewidth=1, alpha=0.7)
    axs[2].set_title('Spectrum Comparison')
    axs[2].set_xlabel('Frequency (Hz)')
    axs[2].set_ylabel('Magnitude')
    axs[2].legend()
    axs[2].grid(True, alpha=0.3)
    axs[2].set_xlim([0, 1000])
    
    plt.tight_layout()
    plt.savefig(output_plot, dpi=100)
    print(f'\\n波形图已保存到: {output_plot}')
    
    return correlation

# 分析失败的案例
ref = 'tests/fixtures/b_freq_tests/b_freq_0.4958.wav'
test = 'tests/output/test_b_freq_0.4958.wav'

correlation = analyze_waveform_diff(ref, test)
