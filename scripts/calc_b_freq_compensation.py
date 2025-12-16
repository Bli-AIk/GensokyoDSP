#!/usr/bin/env python3
"""计算每个b_freq值需要的谐波补偿系数"""

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

def analyze_b_freq_compensation(b_freq_value):
    """分析b_freq补偿需求"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 使用稳定段进行FFT
    start_idx = int(1.0 * ref_rate)
    end_idx = int(3.0 * ref_rate)
    ref_segment = ref_data[start_idx:end_idx]
    gen_segment = gen_data[start_idx:end_idx]
    
    # 计算RMS
    ref_rms = np.sqrt(np.mean(ref_segment**2))
    gen_rms = np.sqrt(np.mean(gen_segment**2))
    rms_ratio = gen_rms / ref_rms
    
    # FFT
    ref_fft = fft.rfft(ref_segment)
    gen_fft = fft.rfft(gen_segment)
    ref_freqs = fft.rfftfreq(len(ref_segment), 1/ref_rate)
    gen_freqs = fft.rfftfreq(len(gen_segment), 1/gen_rate)
    ref_mag = np.abs(ref_fft)
    gen_mag = np.abs(gen_fft)
    
    # 找基频
    ref_peak_idx = np.argmax(ref_mag)
    fundamental = ref_freqs[ref_peak_idx]
    
    # 计算谐波能量
    def get_harmonic_energy(freqs, mag, fund, max_h=10):
        total = 0
        for n in range(1, max_h + 1):
            target = fund * n
            mask = (freqs >= target - 20) & (freqs <= target + 20)
            if np.any(mask):
                total += np.max(mag[mask])
        return total
    
    ref_energy = get_harmonic_energy(ref_freqs, ref_mag, fundamental)
    gen_energy = get_harmonic_energy(gen_freqs, gen_mag, fundamental)
    energy_ratio = gen_energy / ref_energy
    
    # 计算需要的增益
    # 如果只看RMS，需要的增益是 1/rms_ratio
    # 但如果谐波能量比RMS更低，说明需要更多补偿
    needed_gain = 1.0 / rms_ratio
    harmonic_gain = 1.0 / energy_ratio
    
    return {
        'b_freq': float(b_freq_value),
        'fundamental': fundamental,
        'rms_ratio': rms_ratio,
        'energy_ratio': energy_ratio,
        'needed_rms_gain': needed_gain,
        'needed_harmonic_gain': harmonic_gain,
        'current_compensation': None  # 会在后面填充
    }

def main():
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    results = []
    for b_freq_value in b_freq_values:
        result = analyze_b_freq_compensation(b_freq_value)
        if result:
            results.append(result)
    
    if not results:
        return
    
    # 从代码中读取当前的补偿值
    freq_to_compensation = {
        65.4: 0.7072 * 1.0114,
        130.5: 0.7885 * 1.0114,
        514.1: 0.8439 * 1.0114 + (514.1 - 253.2) / (1200.0 - 253.2) * (1.05 - 0.8439) * 1.0114,
        645.9: 0.8439 * 1.0114 + (645.9 - 253.2) / (1200.0 - 253.2) * (1.05 - 0.8439) * 1.0114,
        984.2: 0.8439 * 1.0114 + (984.2 - 253.2) / (1200.0 - 253.2) * (1.05 - 0.8439) * 1.0114,
        2093.0: 1.1111 * 1.0114 + (2093.0 - 2093.0) / (4000.0 - 2093.0) * (1.34 - 1.1111) * 1.0114,
        3754.3: 1.3188 * 1.0114 + (3754.3 - 3754.3) / (6000.0 - 3754.3) * (1.60 - 1.3188) * 1.0114,
        5569.6: 1.5707 * 1.0114,
    }
    
    for r in results:
        # 找最接近的频率
        closest_freq = min(freq_to_compensation.keys(), key=lambda x: abs(x - r['fundamental']))
        r['current_compensation'] = freq_to_compensation[closest_freq]
    
    print("="*100)
    print("b_freq测试补偿分析")
    print("="*100)
    print(f"{'b_freq':<8} | {'Freq(Hz)':<10} | {'RMS Ratio':<10} | {'Harm Ratio':<10} | {'Current':<10} | {'Need RMS':<10} | {'Need Harm':<10}")
    print("-"*100)
    
    for r in results:
        print(f"{r['b_freq']:<8.4f} | {r['fundamental']:<10.1f} | {r['rms_ratio']:<10.4f} | {r['energy_ratio']:<10.4f} | {r['current_compensation']:<10.4f} | {r['needed_rms_gain']:<10.4f} | {r['needed_harmonic_gain']:<10.4f}")
    
    print("\n" + "="*100)
    print("建议的新补偿值（基于谐波能量）:")
    print("="*100)
    
    for r in results:
        new_compensation = r['current_compensation'] * r['needed_harmonic_gain'] / r['needed_rms_gain']
        print(f"  {r['fundamental']:>7.1f} Hz (b_freq={r['b_freq']:.4f}): 当前={r['current_compensation']:.4f}, 建议={new_compensation:.4f}")

if __name__ == "__main__":
    main()
