#!/usr/bin/env python3
"""分析b_freq测试的包络问题"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.io.wavfile as wavfile

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def analyze_envelope(data, rate, window_ms=10):
    """分析包络"""
    window_samples = int(window_ms * rate / 1000)
    envelope = []
    times = []
    
    for i in range(0, len(data) - window_samples, window_samples // 2):
        segment = data[i:i+window_samples]
        rms = np.sqrt(np.mean(segment**2))
        envelope.append(rms)
        times.append(i / rate)
    
    return np.array(times), np.array(envelope)

def main():
    b_freq_values = ['0.4958', '0.5506', '0.6519', '0.8080', '0.8502', '0.9051']
    
    Path('temps').mkdir(exist_ok=True)
    
    for b_freq_value in b_freq_values:
        ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value}.wav")
        gen_file = Path(f"tests/output/test_b_freq_{b_freq_value}.wav")
        
        if not ref_file.exists() or not gen_file.exists():
            print(f"跳过 b_freq={b_freq_value} (文件不存在)")
            continue
        
        # 加载音频
        ref_rate, ref_data = load_wav(ref_file)
        gen_rate, gen_data = load_wav(gen_file)
        
        # 分析包络
        ref_times, ref_env = analyze_envelope(ref_data, ref_rate)
        gen_times, gen_env = analyze_envelope(gen_data, gen_rate)
        
        # 找到峰值
        ref_peak_idx = np.argmax(ref_env)
        gen_peak_idx = np.argmax(gen_env)
        ref_peak_time = ref_times[ref_peak_idx]
        gen_peak_time = gen_times[gen_peak_idx]
        ref_peak_val = ref_env[ref_peak_idx]
        gen_peak_val = gen_env[gen_peak_idx]
        
        # 绘制包络对比
        plt.figure(figsize=(15, 6))
        
        # 全包络
        plt.subplot(1, 2, 1)
        plt.plot(ref_times, ref_env, 'b-', label='Reference', linewidth=2)
        plt.plot(gen_times, gen_env, 'r-', label='Generated', linewidth=2)
        plt.axvline(ref_peak_time, color='b', linestyle='--', alpha=0.5, 
                   label=f'Ref peak: {ref_peak_time:.3f}s, {ref_peak_val:.4f}')
        plt.axvline(gen_peak_time, color='r', linestyle='--', alpha=0.5,
                   label=f'Gen peak: {gen_peak_time:.3f}s, {gen_peak_val:.4f}')
        plt.xlabel('Time (s)')
        plt.ylabel('RMS Envelope')
        plt.title(f'b_freq={b_freq_value} - Full Envelope')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 前0.5秒（起音阶段）
        plt.subplot(1, 2, 2)
        max_time = 0.5
        ref_mask = ref_times <= max_time
        gen_mask = gen_times <= max_time
        plt.plot(ref_times[ref_mask], ref_env[ref_mask], 'b-', label='Reference', linewidth=2)
        plt.plot(gen_times[gen_mask], gen_env[gen_mask], 'r-', label='Generated', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('RMS Envelope')
        plt.title(f'b_freq={b_freq_value} - Attack Phase (0-0.5s)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'temps/b_freq_{b_freq_value}_envelope.png', dpi=150)
        plt.close()
        
        print(f"b_freq={b_freq_value}:")
        print(f"  参考峰值: 时间={ref_peak_time:.3f}s, 值={ref_peak_val:.4f}")
        print(f"  生成峰值: 时间={gen_peak_time:.3f}s, 值={gen_peak_val:.4f}")
        print(f"  峰值比率: {gen_peak_val / ref_peak_val:.4f}")
        print(f"  时间差异: {abs(gen_peak_time - ref_peak_time):.3f}s")
        print()

if __name__ == "__main__":
    main()
