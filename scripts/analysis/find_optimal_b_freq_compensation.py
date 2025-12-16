#!/usr/bin/env python3
"""
找出每个b_freq测试的最佳补偿值
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

def analyze_all_b_freq():
    """分析所有b_freq测试"""
    base_path = Path("/workspaces/GensokyoDSP")
    freq_a = 523.25
    
    # 所有b_freq测试值和对应的ratio（从synthesizer.rs的quantize_b_freq_ratio）
    all_tests = [
        ('0.0547', 1.0),       # < 0.48: unison
        ('0.1058', 1.0),
        ('0.1496', 1.0),
        ('0.2007', 1.0),
        ('0.2518', 1.0),
        ('0.3102', 1.0),
        ('0.3540', 1.0),
        ('0.4051', 1.0),
        ('0.4536', 1.0),
        ('0.4958', 0.12497),   # 0.48-0.52: 1/8
        ('0.5506', 0.24939),   # 0.52-0.57: 130Hz
        ('0.6055', 0.48381),   # 0.57-0.62: 253Hz
        ('0.6519', 0.48381),
        ('0.7025', 0.58891),   # 0.62-0.67: 308Hz
        ('0.7489', 1.0),       # 0.67-0.69: unison
        ('0.8080', 4.0),       # 0.77-0.82: 2x octave
        ('0.8502', 7.17497),   # 0.82-0.87: 3754Hz
        ('0.9051', 10.64416),  # 0.87-0.92: 5569Hz
        ('0.9515', 16.09951),  # 0.92-0.97: 8424Hz
        ('1.0', 32.0),         # >= 0.97: 16744Hz
    ]
    
    print("所有b_freq测试分析:")
    print("=" * 110)
    print(f"{'b_freq':<10} {'频率B':<10} {'参考RMS':<12} {'测试RMS':<12} {'当前补偿':<12} {'需要补偿':<12} {'状态':<10}")
    print("-" * 110)
    
    failed_tests = []
    
    for value, ratio in all_tests:
        ref_file = base_path / "tests" / "fixtures" / "b_freq_tests" / f"b_freq_{value}.wav"
        test_file = base_path / "tests" / "output" / f"test_b_freq_{value}.wav"
        
        if not ref_file.exists() or not test_file.exists():
            continue
        
        ref_data, _ = read_wav(ref_file)
        test_data, _ = read_wav(test_file)
        
        # 使用稳态RMS（后半段）
        half = len(ref_data) // 2
        ref_rms = np.sqrt(np.mean(ref_data[half:]**2))
        test_rms = np.sqrt(np.mean(test_data[half:]**2))
        
        freq_b = freq_a * ratio
        
        # 估算当前补偿
        if freq_b < 150.0:
            t = (freq_b - 65.0) / (150.0 - 65.0)
            current_comp = 0.8125 + t * (0.85 - 0.8125)
        elif freq_b < 300.0:
            t = (freq_b - 150.0) / (300.0 - 150.0)
            current_comp = 0.85 + t * (0.89 - 0.85)
        elif freq_b < 1500.0:
            t = (freq_b - 300.0) / (1500.0 - 300.0)
            current_comp = 0.89 + t * (1.0 - 0.89)
        elif freq_b < 3000.0:
            t = (freq_b - 1500.0) / (3000.0 - 1500.0)
            current_comp = 1.0 + t * (0.98 - 1.0)
        elif freq_b < 5000.0:
            t = (freq_b - 3000.0) / (5000.0 - 3000.0)
            current_comp = 0.98 + t * (0.94 - 0.98)
        elif freq_b < 6000.0:
            t = (freq_b - 5000.0) / (6000.0 - 5000.0)
            current_comp = 0.94 + t * (0.95 - 0.94)
        else:
            current_comp = 0.95 + ((freq_b - 6000.0) / 2000.0) * 0.02
        
        ratio_current = test_rms / ref_rms
        needed_comp = current_comp / ratio_current
        
        status = "PASS" if ratio_current >= 0.95 and ratio_current <= 1.05 else "FAIL"
        if status == "FAIL":
            failed_tests.append({
                'value': value,
                'freq_b': freq_b,
                'ratio': ratio,
                'current': current_comp,
                'needed': needed_comp,
                'test_rms': test_rms,
                'ref_rms': ref_rms,
            })
        
        print(f"{value:<10} {freq_b:<10.2f} {ref_rms:<12.6f} {test_rms:<12.6f} "
              f"{current_comp:<12.4f} {needed_comp:<12.4f} {status:<10}")
    
    if failed_tests:
        print("\n" + "=" * 110)
        print("失败测试的建议修正:")
        print("=" * 110)
        for test in failed_tests:
            print(f"\nb_freq={test['value']} (频率B={test['freq_b']:.2f}Hz):")
            print(f"  当前补偿: {test['current']:.4f}")
            print(f"  需要补偿: {test['needed']:.4f}")
            print(f"  调整量: {test['needed'] - test['current']:+.4f}")
            print(f"  测试/参考RMS比: {test['test_rms']/test['ref_rms']:.4f}")

if __name__ == "__main__":
    analyze_all_b_freq()
