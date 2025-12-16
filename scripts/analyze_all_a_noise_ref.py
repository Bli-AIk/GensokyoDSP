#!/usr/bin/env python3
"""分析所有a_noise参考文件的包络特征"""

import numpy as np
from pathlib import Path
import scipy.io.wavfile as wavfile

def load_wav(filepath):
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    return rate, data.astype(np.float32) / 32768.0

def compute_envelope(data, rate):
    window_ms = 10
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

# 所有a_noise值
a_noise_values = [
    0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 0.3540, 0.4051,
    0.4536, 0.4958, 0.5506, 0.6055, 0.6519, 0.7025, 0.7489, 0.8080,
    0.8502, 0.9051, 0.9515, 1.0
]

print('=' * 80)
print('所有a_noise参考文件的包络特征')
print('=' * 80)
print(f'{"a_noise":>8} | {"Attack(s)":>10} | {"Peak":>10} | {"Avg RMS":>10} | {"Crest":>8}')
print('-' * 80)

results = []
for a_noise in a_noise_values:
    ref_file = Path(f'tests/fixtures/a_noise_tests/a_noise_{a_noise}.wav')
    if ref_file.exists():
        rate, data = load_wav(ref_file)
        times, env = compute_envelope(data, rate)
        peak_idx = np.argmax(env)
        attack_time = times[peak_idx]
        peak_level = env[peak_idx]
        avg_rms = np.mean(env)
        crest = peak_level / (avg_rms + 1e-10)
        results.append((a_noise, attack_time, peak_level, avg_rms, crest))
        print(f'{a_noise:8.4f} | {attack_time:10.4f} | {peak_level:10.6f} | {avg_rms:10.6f} | {crest:8.4f}')

print('\n' + '=' * 80)
print('模式分析')
print('=' * 80)

# 分组分析
low_noise = [r for r in results if r[0] < 0.8]
high_noise = [r for r in results if r[0] >= 0.8]

print(f'\n低噪声组 (a_noise < 0.8, n={len(low_noise)}):')
if low_noise:
    attacks = [r[1] for r in low_noise]
    print(f'  Attack时间范围: {min(attacks):.4f}s - {max(attacks):.4f}s')
    print(f'  Attack时间平均: {np.mean(attacks):.4f}s')

print(f'\n高噪声组 (a_noise >= 0.8, n={len(high_noise)}):')
if high_noise:
    attacks = [r[1] for r in high_noise]
    print(f'  Attack时间范围: {min(attacks):.4f}s - {max(attacks):.4f}s')
    print(f'  Attack时间平均: {np.mean(attacks):.4f}s')
    print(f'\n高噪声组详细:')
    for r in high_noise:
        print(f'  a_noise={r[0]:.4f}: attack={r[1]:.4f}s')
