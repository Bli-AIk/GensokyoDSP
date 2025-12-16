#!/usr/bin/env python3
"""测试纯粹的锯齿波生成"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_saw_reference(freq, sample_rate, duration, n_harmonics=100):
    """生成标准锯齿波作为参考"""
    t = np.arange(int(duration * sample_rate)) / sample_rate
    saw = np.zeros_like(t)
    
    for n in range(1, n_harmonics + 1):
        amp = (-1)**(n + 1) / n
        saw += amp * np.sin(2 * np.pi * n * freq * t)
    
    saw *= (2.0 / np.pi)
    return t, saw

def main():
    # 生成130Hz锯齿波
    freq = 130.5
    sample_rate = 48000
    duration = 0.01  # 10ms，几个周期
    
    t, ref_saw = generate_saw_reference(freq, sample_rate, duration, n_harmonics=200)
    
    # 绘制波形
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(t * 1000, ref_saw, 'b-', linewidth=2)
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude')
    plt.title(f'Reference Sawtooth @ {freq} Hz')
    plt.grid(True, alpha=0.3)
    
    # 频谱
    from scipy import fft
    fft_result = fft.rfft(ref_saw)
    freqs = fft.rfftfreq(len(ref_saw), 1/sample_rate)
    magnitude = np.abs(fft_result)
    
    plt.subplot(1, 2, 2)
    # 只显示前20个谐波
    for n in range(1, 21):
        target = freq * n
        mask = (freqs >= target - 10) & (freqs <= target + 10)
        if np.any(mask):
            peak_mag = np.max(magnitude[mask])
            plt.stem([n], [peak_mag], basefmt=' ')
    
    plt.xlabel('Harmonic Number')
    plt.ylabel('Magnitude')
    plt.title('Harmonic Spectrum')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('temps/reference_sawtooth.png', dpi=150)
    
    print(f"生成的参考锯齿波:")
    print(f"  频率: {freq} Hz")
    print(f"  RMS: {np.sqrt(np.mean(ref_saw**2)):.4f}")
    print(f"  Peak: {np.max(np.abs(ref_saw)):.4f}")
    
    # 打印前10个谐波的幅度
    print(f"\n谐波幅度:")
    for n in range(1, 11):
        target = freq * n
        mask = (freqs >= target - 10) & (freqs <= target + 10)
        if np.any(mask):
            peak_mag = np.max(magnitude[mask])
            expected_amp = ((-1)**(n+1) / n) * (2.0 / np.pi)
            print(f"  H{n}: mag={peak_mag:.1f}, expected_relative_amp={expected_amp:.4f}")

if __name__ == "__main__":
    Path('temps').mkdir(exist_ok=True)
    main()
