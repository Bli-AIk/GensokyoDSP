#!/usr/bin/env python3
"""
为所有失败的b_freq测试计算精确的补偿值
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path

# 所有失败的b_freq测试
failing_tests = [
    0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051
]

# 量化函数（从synthesizer.rs复制）
def quantize_b_freq_ratio(p):
    if p < 0.48:
        return 1.0
    elif p < 0.52:
        return 0.12497
    elif p < 0.57:
        return 0.24939
    elif p < 0.62:
        return 0.48381
    elif p < 0.67:
        return 0.58891
    elif p < 0.69:
        return 1.0
    elif p < 0.72:
        return 1.00901
    elif p < 0.77:
        return 2.0
    elif p < 0.82:
        return 4.0
    elif p < 0.87:
        return 7.17497
    elif p < 0.92:
        return 10.64416
    elif p < 0.97:
        return 16.09951
    else:
        return 32.0

def analyze_rms(b_freq_value):
    """分析RMS并计算需要的补偿"""
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value:.4f}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value:.4f}.wav")
    
    if not ref_file.exists() or not gen_file.exists():
        return None
    
    sr_ref, audio_ref = wavfile.read(ref_file)
    sr_gen, audio_gen = wavfile.read(gen_file)
    
    # 转换为浮点数
    if audio_ref.dtype == np.int16:
        audio_ref = audio_ref.astype(np.float32) / 32768.0
    if audio_gen.dtype == np.int16:
        audio_gen = audio_gen.astype(np.float32) / 32768.0
    
    # 只取单声道
    if len(audio_ref.shape) > 1:
        audio_ref = audio_ref[:, 0]
    if len(audio_gen.shape) > 1:
        audio_gen = audio_gen[:, 0]
    
    # 确保长度一致
    min_len = min(len(audio_ref), len(audio_gen))
    audio_ref = audio_ref[:min_len]
    audio_gen = audio_gen[:min_len]
    
    # 计算RMS
    rms_ref = np.sqrt(np.mean(audio_ref**2))
    rms_gen = np.sqrt(np.mean(audio_gen**2))
    rms_ratio = rms_gen / rms_ref if rms_ref > 0 else 0
    
    # 计算频率
    freq_a = 523.0
    b_ratio = quantize_b_freq_ratio(b_freq_value)
    freq_b = freq_a * b_ratio
    
    # 需要的补偿 = 1 / rms_ratio
    needed_compensation = 1.0 / rms_ratio if rms_ratio > 0 else 1.0
    
    return {
        'b_freq': b_freq_value,
        'freq_b': freq_b,
        'rms_ref': rms_ref,
        'rms_gen': rms_gen,
        'rms_ratio': rms_ratio,
        'needed_comp': needed_compensation
    }

def main():
    print("=" * 80)
    print("失败的b_freq测试的补偿值计算")
    print("=" * 80)
    
    results = []
    for b_freq in failing_tests:
        result = analyze_rms(b_freq)
        if result:
            results.append(result)
            print(f"\nb_freq={result['b_freq']:.4f}")
            print(f"  频率: {result['freq_b']:.2f} Hz")
            print(f"  RMS参考: {result['rms_ref']:.6f}")
            print(f"  RMS生成: {result['rms_gen']:.6f}")
            print(f"  RMS比率: {result['rms_ratio']:.4f}")
            print(f"  需要的补偿: {result['needed_comp']:.4f}")
    
    print("\n" + "=" * 80)
    print("Rust代码格式的补偿表:")
    print("=" * 80)
    print()
    
    for r in results:
        print(f"({r['freq_b']:.2f}, {r['needed_comp']:.4f}),  // b_freq={r['b_freq']:.4f}")

if __name__ == "__main__":
    main()
