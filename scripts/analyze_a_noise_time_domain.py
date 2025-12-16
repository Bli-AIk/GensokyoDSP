#!/usr/bin/env python3
"""深入分析a_noise高值时的实际音频特征"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.io.wavfile as wavfile

def load_wav(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def analyze_time_domain(a_noise_value):
    ref_file = Path(f"tests/fixtures/a_noise_tests/a_noise_{a_noise_value}.wav")
    gen_file = Path(f"tests/output/test_a_noise_{a_noise_value}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    rate, ref_data = load_wav(ref_file)
    _, gen_data = load_wav(gen_file)
    
    # 计算短时RMS (50ms窗口)
    window_ms = 50
    window_samples = int(rate * window_ms / 1000)
    hop_samples = window_samples // 4
    
    def compute_rms_envelope(data):
        envelope = []
        times = []
        for i in range(0, len(data) - window_samples, hop_samples):
            window = data[i:i + window_samples]
            rms = np.sqrt(np.mean(window**2))
            envelope.append(rms)
            times.append(i / rate)
        return np.array(times), np.array(envelope)
    
    ref_times, ref_env = compute_rms_envelope(ref_data)
    gen_times, gen_env = compute_rms_envelope(gen_data)
    
    # 绘制前5秒的详细包络
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    
    # 参考
    mask = ref_times <= 5.0
    axes[0].plot(ref_times[mask], ref_env[mask], 'b-', linewidth=1.5, label='RMS Envelope')
    axes[0].set_title(f'Reference: a_noise={a_noise_value}')
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('RMS')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    # 生成
    mask = gen_times <= 5.0
    axes[1].plot(gen_times[mask], gen_env[mask], 'r-', linewidth=1.5, label='RMS Envelope')
    axes[1].set_title(f'Generated: a_noise={a_noise_value}')
    axes[1].set_xlabel('Time (s)')
    axes[1].set_ylabel('RMS')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(f'temps/a_noise_{a_noise_value}_time_analysis.png', dpi=150)
    plt.close()
    
    # 统计分析
    print(f"\\na_noise={a_noise_value}:")
    print(f"  参考音频:")
    print(f"    RMS范围: {np.min(ref_env):.6f} - {np.max(ref_env):.6f}")
    print(f"    平均RMS: {np.mean(ref_env):.6f}")
    print(f"    初始RMS (0-0.5s): {np.mean(ref_env[:min(len(ref_env), int(0.5*len(ref_env)/ref_times[-1]))]):.6f}")
    print(f"  生成音频:")
    print(f"    RMS范围: {np.min(gen_env):.6f} - {np.max(gen_env):.6f}")
    print(f"    平均RMS: {np.mean(gen_env):.6f}")
    print(f"    初始RMS (0-0.5s): {np.mean(gen_env[:min(len(gen_env), int(0.5*len(gen_env)/gen_times[-1]))]):.6f}")
    
    return {
        'ref_env_std': np.std(ref_env),
        'gen_env_std': np.std(gen_env),
    }

# 分析失败的测试
Path('temps').mkdir(exist_ok=True)

print("=" * 80)
print("a_noise高值时域分析")
print("=" * 80)

for a_noise in [0.8502, 0.9051, 0.9515, 1.0]:
    analyze_time_domain(a_noise)
