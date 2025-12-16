#!/usr/bin/env python3
"""对比通过和失败的b_freq测试"""

import numpy as np
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import fft

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def analyze(b_freq_value, label):
    """分析b_freq测试"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        print(f"{label}: 文件不存在")
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 使用稳定段
    start_idx = int(1.0 * ref_rate)
    end_idx = int(3.0 * ref_rate)
    ref_seg = ref_data[start_idx:end_idx]
    gen_seg = gen_data[start_idx:end_idx]
    
    # 计算相关系数
    rms_ref = np.sqrt(np.mean(ref_seg**2))
    rms_gen = np.sqrt(np.mean(gen_seg**2))
    
    if rms_ref > 0 and rms_gen > 0:
        corr = np.mean(ref_seg * gen_seg) / (rms_ref * rms_gen)
        similarity = (corr + 1.0) / 2.0 * 100.0
    else:
        corr = 0.0
        similarity = 0.0
    
    # FFT
    ref_fft = fft.rfft(ref_seg)
    gen_fft = fft.rfft(gen_seg)
    ref_freqs = fft.rfftfreq(len(ref_seg), 1/ref_rate)
    ref_mag = np.abs(ref_fft)
    gen_mag = np.abs(gen_fft)
    
    # 找基频
    peak_idx = np.argmax(ref_mag)
    fundamental = ref_freqs[peak_idx]
    
    print(f"\n{label} (b_freq={b_freq_value}, 基频={fundamental:.1f} Hz):")
    print(f"  RMS比: {rms_gen/rms_ref:.4f}")
    print(f"  相关系数: {corr:.4f}")
    print(f"  相似度: {similarity:.2f}%")
    
    # 分析前几个谐波
    print(f"  前5个谐波:")
    for n in range(1, 6):
        target = fundamental * n
        mask = (ref_freqs >= target - 20) & (ref_freqs <= target + 20)
        if np.any(mask):
            local_idx = np.where(mask)[0][np.argmax(ref_mag[mask])]
            ref_complex = ref_fft[local_idx]
            gen_complex = gen_fft[local_idx]
            
            ref_amp = np.abs(ref_complex)
            gen_amp = np.abs(gen_complex)
            ref_phase = np.angle(ref_complex, deg=True)
            gen_phase = np.angle(gen_complex, deg=True)
            
            phase_diff = gen_phase - ref_phase
            while phase_diff > 180:
                phase_diff -= 360
            while phase_diff < -180:
                phase_diff += 360
            
            mag_ratio = gen_amp / (ref_amp + 1e-10)
            print(f"    H{n}: mag_ratio={mag_ratio:.4f}, phase_diff={phase_diff:6.1f}°")

def main():
    # 对比通过和失败的测试
    analyze("0.2518", "通过")
    analyze("0.4958", "失败")
    analyze("0.8080", "失败")

if __name__ == "__main__":
    main()
