#!/usr/bin/env python3
"""深入分析a_noise高值测试的包络特征"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import signal

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def compute_envelope(data, rate, window_ms=10):
    """计算RMS包络"""
    window_samples = int(rate * window_ms / 1000)
    hop_samples = window_samples // 2
    
    envelope = []
    times = []
    
    for i in range(0, len(data) - window_samples, hop_samples):
        window = data[i:i + window_samples]
        rms = np.sqrt(np.mean(window**2))
        envelope.append(rms)
        times.append(i / rate)
    
    return np.array(times), np.array(envelope)

def analyze_a_noise_envelope(a_noise_value):
    """分析特定a_noise值的包络"""
    ref_file = Path(f"tests/fixtures/a_noise_tests/a_noise_{a_noise_value}.wav")
    gen_file = Path(f"tests/output/test_a_noise_{a_noise_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        print(f"文件不存在: a_noise={a_noise_value}")
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    # 计算包络
    ref_times, ref_env = compute_envelope(ref_data, ref_rate)
    gen_times, gen_env = compute_envelope(gen_data, gen_rate)
    
    # 查找攻击时间（达到峰值的时间）
    ref_peak_idx = np.argmax(ref_env)
    gen_peak_idx = np.argmax(gen_env)
    
    ref_attack_time = ref_times[ref_peak_idx]
    gen_attack_time = gen_times[gen_peak_idx]
    
    ref_peak_level = ref_env[ref_peak_idx]
    gen_peak_level = gen_env[gen_peak_idx]
    
    # 查找10%峰值的时间点
    ref_10pct_idx = np.where(ref_env >= ref_peak_level * 0.1)[0]
    gen_10pct_idx = np.where(gen_env >= gen_peak_level * 0.1)[0]
    
    ref_10pct_time = ref_times[ref_10pct_idx[0]] if len(ref_10pct_idx) > 0 else 0
    gen_10pct_time = gen_times[gen_10pct_idx[0]] if len(gen_10pct_idx) > 0 else 0
    
    # 查找90%峰值的时间点
    ref_90pct_idx = np.where(ref_env >= ref_peak_level * 0.9)[0]
    gen_90pct_idx = np.where(gen_env >= gen_peak_level * 0.9)[0]
    
    ref_90pct_time = ref_times[ref_90pct_idx[0]] if len(ref_90pct_idx) > 0 else 0
    gen_90pct_time = gen_times[gen_90pct_idx[0]] if len(gen_90pct_idx) > 0 else 0
    
    # 查找衰减时间（从峰值到50%）
    ref_decay_idx = np.where((ref_times > ref_attack_time) & (ref_env <= ref_peak_level * 0.5))[0]
    gen_decay_idx = np.where((gen_times > gen_attack_time) & (gen_env <= gen_peak_level * 0.5))[0]
    
    ref_decay_time = ref_times[ref_decay_idx[0]] - ref_attack_time if len(ref_decay_idx) > 0 else 0
    gen_decay_time = gen_times[gen_decay_idx[0]] - gen_attack_time if len(gen_decay_idx) > 0 else 0
    
    results = {
        'a_noise': a_noise_value,
        'ref_peak_level': ref_peak_level,
        'gen_peak_level': gen_peak_level,
        'ref_attack_time': ref_attack_time,
        'gen_attack_time': gen_attack_time,
        'ref_10_90_time': ref_90pct_time - ref_10pct_time,
        'gen_10_90_time': gen_90pct_time - gen_10pct_time,
        'ref_decay_time': ref_decay_time,
        'gen_decay_time': gen_decay_time,
        'ref_avg_rms': np.mean(ref_env),
        'gen_avg_rms': np.mean(gen_env),
    }
    
    # 绘制对比图
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(ref_times[:1000], ref_env[:1000], 'b-', label='Reference', linewidth=2)
    plt.plot(gen_times[:1000], gen_env[:1000], 'r--', label='Generated', linewidth=2)
    plt.axvline(ref_attack_time, color='b', linestyle=':', alpha=0.5)
    plt.axvline(gen_attack_time, color='r', linestyle=':', alpha=0.5)
    plt.xlabel('Time (s)')
    plt.ylabel('RMS Envelope')
    plt.title(f'a_noise={a_noise_value} - Attack Phase')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(ref_times, ref_env, 'b-', label='Reference', linewidth=2)
    plt.plot(gen_times, gen_env, 'r--', label='Generated', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('RMS Envelope')
    plt.title(f'a_noise={a_noise_value} - Full Duration')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'temps/a_noise_{a_noise_value}_envelope.png', dpi=150)
    plt.close()
    
    return results

def main():
    print("=" * 80)
    print("a_noise高值测试包络分析")
    print("=" * 80)
    
    Path('temps').mkdir(exist_ok=True)
    
    a_noise_values = [0.8502, 0.9051, 0.9515, 1.0]
    
    all_results = []
    for a_noise_value in a_noise_values:
        print(f"\n分析 a_noise={a_noise_value}...")
        results = analyze_a_noise_envelope(a_noise_value)
        if results:
            all_results.append(results)
            print(f"  参考峰值: {results['ref_peak_level']:.6f}")
            print(f"  生成峰值: {results['gen_peak_level']:.6f}")
            print(f"  参考attack时间: {results['ref_attack_time']:.4f}s")
            print(f"  生成attack时间: {results['gen_attack_time']:.4f}s")
            print(f"  参考10-90%时间: {results['ref_10_90_time']:.4f}s")
            print(f"  生成10-90%时间: {results['gen_10_90_time']:.4f}s")
            print(f"  参考平均RMS: {results['ref_avg_rms']:.6f}")
            print(f"  生成平均RMS: {results['gen_avg_rms']:.6f}")
    
    if all_results:
        print("\n" + "=" * 80)
        print("包络时间趋势:")
        print("=" * 80)
        print("a_noise | Ref Attack | Gen Attack | Ref 10-90% | Gen 10-90%")
        print("-" * 80)
        for r in all_results:
            print(f"{r['a_noise']:.4f} | {r['ref_attack_time']:10.4f} | {r['gen_attack_time']:10.4f} | "
                  f"{r['ref_10_90_time']:10.4f} | {r['gen_10_90_time']:10.4f}")

if __name__ == "__main__":
    main()
