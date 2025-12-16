#!/usr/bin/env python3
"""计算b_freq补偿值"""
import numpy as np
import wave
import struct
import os

def load_wav(filepath):
    """加载WAV文件"""
    with wave.open(filepath, 'rb') as wav:
        nchannels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        framerate = wav.getframerate()
        nframes = wav.getnframes()
        
        frames = wav.readframes(nframes)
        
        if sampwidth == 2:
            data = struct.unpack(f'{nframes * nchannels}h', frames)
        elif sampwidth == 4:
            data = struct.unpack(f'{nframes * nchannels}i', frames)
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")
        
        samples = np.array(data, dtype=float)
        
        if sampwidth == 2:
            samples = samples / 32768.0
        elif sampwidth == 4:
            samples = samples / 2147483648.0
        
        if nchannels == 2:
            samples = samples.reshape(-1, 2)
            samples = samples[:, 0]
        
        return samples, framerate

def calculate_steady_state_rms(samples, start_ratio=0.5):
    """计算稳态RMS（后半段）"""
    start = int(len(samples) * start_ratio)
    return np.sqrt(np.mean(samples[start:]**2))

# b_freq测试参数到频率的映射
b_freq_map = {
    0.4958: 514.1483 * 0.12497,  # ~64 Hz
    0.5506: 645.8984 * 0.24939,  # ~161 Hz  
    0.6519: 984.1547 * 0.48381,  # ~476 Hz
    0.8080: 1883.8349 * 4.0,     # ~7535 Hz
    0.8502: 2245.1954 * 4.0,     # ~8980 Hz
    0.9051: 2820.5016 * 4.0,     # ~11282 Hz
}

print("=" * 80)
print("计算b_freq频率补偿值")
print("=" * 80)

results = []

for b_freq_val, freq_b in b_freq_map.items():
    test_name = f"b_freq_{b_freq_val:.4f}"
    ref_file = f"tests/fixtures/b_freq_tests/{test_name}.wav"
    test_file = f"tests/output/test_{test_name}.wav"
    
    if not os.path.exists(ref_file) or not os.path.exists(test_file):
        print(f"\n{test_name}: 文件缺失")
        continue
    
    ref_samples, _ = load_wav(ref_file)
    test_samples, _ = load_wav(test_file)
    
    ref_steady = calculate_steady_state_rms(ref_samples)
    test_steady = calculate_steady_state_rms(test_samples)
    
    ratio = test_steady / ref_steady
    needed_compensation = 1.0 / ratio
    
    results.append({
        'b_freq': b_freq_val,
        'freq_b': freq_b,
        'ref_steady': ref_steady,
        'test_steady': test_steady,
        'ratio': ratio,
        'needed': needed_compensation
    })
    
    print(f"\n{test_name}:")
    print(f"  频率B: {freq_b:.1f} Hz")
    print(f"  参考稳态RMS: {ref_steady:.6f}")
    print(f"  测试稳态RMS: {test_steady:.6f}")
    print(f"  测试/参考比率: {ratio:.4f}")
    print(f"  需要的补偿: {needed_compensation:.4f}x")

print("\n" + "=" * 80)
print("补偿值总结")
print("=" * 80)
print(f"{'频率B (Hz)':<12} {'当前测试/参考':<15} {'需要的补偿':<12}")
print("-" * 80)

for r in results:
    print(f"{r['freq_b']:>10.1f}   {r['ratio']:>13.4f}   {r['needed']:>10.4f}")

# 计算全局乘数
if results:
    avg_needed = np.mean([r['needed'] for r in results])
    print(f"\n平均需要的补偿: {avg_needed:.4f}x")
    print(f"建议：将所有b_freq补偿值乘以 {avg_needed:.4f}")
