#!/usr/bin/env python3
"""
分析a_noise参数对应的正确噪声权重
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

def analyze_a_noise_rms(a_noise_value):
    """分析特定a_noise值的RMS"""
    base_path = Path("/workspaces/GensokyoDSP")
    
    ref_file = base_path / "tests" / "fixtures" / "a_noise_tests" / f"a_noise_{a_noise_value}.wav"
    test_file = base_path / "tests" / "output" / f"test_a_noise_{a_noise_value}.wav"
    
    if not ref_file.exists() or not test_file.exists():
        return None
    
    ref_data, ref_sr = read_wav(ref_file)
    test_data, test_sr = read_wav(test_file)
    
    # 计算整体RMS
    ref_rms = np.sqrt(np.mean(ref_data**2))
    test_rms = np.sqrt(np.mean(test_data**2))
    
    # 计算后半段RMS（包络稳定后）
    half_point = len(ref_data) // 2
    ref_rms_steady = np.sqrt(np.mean(ref_data[half_point:]**2))
    test_rms_steady = np.sqrt(np.mean(test_data[half_point:]**2))
    
    return {
        'value': a_noise_value,
        'ref_rms': ref_rms,
        'test_rms': test_rms,
        'ref_steady': ref_rms_steady,
        'test_steady': test_rms_steady,
        'rms_ratio': test_rms / ref_rms if ref_rms > 0 else 0,
        'steady_ratio': test_rms_steady / ref_rms_steady if ref_rms_steady > 0 else 0,
    }

def main():
    # 测试所有a_noise值
    test_values = [
        '0.0547', '0.1058', '0.1496', '0.2007', '0.2518',
        '0.3102', '0.3540', '0.4051', '0.4536', '0.4958',
        '0.5506', '0.6055', '0.6519', '0.7025', '0.7489',
        '0.8080', '0.8502', '0.9051', '0.9515', '1.0'
    ]
    
    results = []
    for value in test_values:
        result = analyze_a_noise_rms(value)
        if result:
            results.append(result)
    
    print("\na_noise RMS分析:")
    print("=" * 90)
    print(f"{'值':<10} {'参考RMS':<12} {'测试RMS':<12} {'RMS比例':<12} {'稳态比例':<12}")
    print("-" * 90)
    
    for r in results:
        print(f"{r['value']:<10} {r['ref_rms']:<12.6f} {r['test_rms']:<12.6f} "
              f"{r['rms_ratio']:<12.3f} {r['steady_ratio']:<12.3f}")
    
    # 分析高噪声值的权重要求
    print("\n\n高噪声值分析 (a_noise >= 0.8):")
    print("=" * 70)
    high_noise = [r for r in results if float(r['value']) >= 0.8]
    
    for r in high_noise:
        # 当前代码: 0.8-1.0 之间线性从0到0.118
        current_t = (float(r['value']) - 0.8) / 0.2
        current_weight = current_t * 0.118
        
        # 需要的权重: 基于RMS比例反推
        needed_weight = current_weight / r['steady_ratio'] if r['steady_ratio'] > 0 else 0
        
        print(f"\na_noise={r['value']}:")
        print(f"  当前权重: {current_weight:.6f}")
        print(f"  稳态RMS比例: {r['steady_ratio']:.3f}")
        print(f"  建议权重: {needed_weight:.6f} (修正因子: {needed_weight/current_weight if current_weight > 0 else 0:.3f})")

if __name__ == "__main__":
    main()
