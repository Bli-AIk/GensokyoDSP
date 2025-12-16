#!/usr/bin/env python3
"""
分析所有a_noise值的起音时间
"""

import numpy as np
import wave
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(str(filename), 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        frames = wav.readframes(n_frames)
        
        if sample_width == 2:
            data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:
            data = np.frombuffer(frames, dtype=np.int32)
        else:
            raise ValueError(f"不支持的采样位深: {sample_width}")
        
        data = data.astype(np.float64) / (2**(sample_width * 8 - 1))
        
        if n_channels == 2:
            data = data[::2]
        
        return data, framerate

def extract_envelope(data, sr, window_ms=10):
    """提取音频的包络"""
    window_samples = int(window_ms * sr / 1000)
    hop = window_samples // 2
    
    times = []
    envelope = []
    
    for i in range(0, len(data) - window_samples, hop):
        segment = data[i:i+window_samples]
        rms = np.sqrt(np.mean(segment**2))
        times.append(i / sr)
        envelope.append(rms)
    
    return np.array(times), np.array(envelope)

def analyze_attack_time(a_noise_value):
    """分析特定a_noise值的起音时间"""
    base_path = Path("/workspaces/GensokyoDSP")
    
    ref_file = base_path / "tests" / "fixtures" / "a_noise_tests" / f"a_noise_{a_noise_value}.wav"
    
    if not ref_file.exists():
        return None
    
    ref_data, ref_sr = read_wav(ref_file)
    ref_times, ref_env = extract_envelope(ref_data, ref_sr)
    
    ref_max = np.max(ref_env)
    
    # 找到达到90%最大值的时间
    ninety_idx = np.where(ref_env >= ref_max * 0.9)[0]
    attack_90 = ref_times[ninety_idx[0]] if len(ninety_idx) > 0 else 0
    
    # 找到达到50%最大值的时间
    half_idx = np.where(ref_env >= ref_max * 0.5)[0]
    attack_50 = ref_times[half_idx[0]] if len(half_idx) > 0 else 0
    
    return {
        'value': a_noise_value,
        'attack_50': attack_50,
        'attack_90': attack_90,
        'max_rms': ref_max,
    }

def main():
    test_values = [
        '0.0547', '0.1058', '0.1496', '0.2007', '0.2518',
        '0.3102', '0.3540', '0.4051', '0.4536', '0.4958',
        '0.5506', '0.6055', '0.6519', '0.7025', '0.7489',
        '0.8080', '0.8502', '0.9051', '0.9515', '1.0'
    ]
    
    results = []
    for value in test_values:
        result = analyze_attack_time(value)
        if result:
            results.append(result)
    
    print("\na_noise值与起音时间分析:")
    print("=" * 70)
    print(f"{'a_noise':<10} {'50%时间':<12} {'90%时间':<12} {'最大RMS':<12}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['value']:<10} {r['attack_50']:<12.3f} {r['attack_90']:<12.3f} {r['max_rms']:<12.6f}")
    
    # 分析趋势
    print("\n\n趋势分析:")
    values_float = [float(r['value']) for r in results]
    attack_90_times = [r['attack_90'] for r in results]
    
    # 找出起音时间突然增加的点
    for i in range(1, len(results)):
        if attack_90_times[i] > attack_90_times[i-1] * 2:
            print(f"起音时间显著增加: a_noise从{results[i-1]['value']}到{results[i]['value']}")
            print(f"  90%时间: {attack_90_times[i-1]:.3f}s -> {attack_90_times[i]:.3f}s")

if __name__ == "__main__":
    main()
