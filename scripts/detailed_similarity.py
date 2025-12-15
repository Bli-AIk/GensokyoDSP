#!/usr/bin/env python3
"""详细分析失败测试的相似度"""

import numpy as np
from scipy.io import wavfile

def analyze_similarity(case):
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    out_file = f"tests/output/test_vol_sus_{case}.wav"
    
    ref_rate, ref_data = wavfile.read(ref_file)
    out_rate, out_data = wavfile.read(out_file)
    
    # 转换为浮点数
    if ref_data.dtype == np.int16:
        ref_data = ref_data.astype(np.float32) / 32768.0
    if out_data.dtype == np.int16:
        out_data = out_data.astype(np.float32) / 32768.0
    
    min_len = min(len(ref_data), len(out_data))
    ref_data = ref_data[:min_len]
    out_data = out_data[:min_len]
    
    # 计算交叉相关系数 (这是 audio_compare.rs 使用的方法)
    # 使用前 5 秒数据
    time_to_compare = 5.0
    num_samples = int(min(time_to_compare * ref_rate, len(ref_data)))
    
    ref_compare = ref_data[:num_samples]
    out_compare = out_data[:num_samples]
    
    # 计算 RMS
    rms_ref = np.sqrt(np.mean(ref_compare**2))
    rms_out = np.sqrt(np.mean(out_compare**2))
    
    # 计算归一化的交叉相关
    correlation = np.mean(ref_compare * out_compare)
    normalized_correlation = correlation / (rms_ref * rms_out) if rms_ref > 0 and rms_out > 0 else 0
    
    # 相似度 (按照 audio_compare.rs 的算法)
    correlation_similarity = (normalized_correlation + 1.0) / 2.0
    similarity = 100.0 * correlation_similarity
    
    print(f"\nvol_sus_{case}:")
    print(f"  RMS (ref): {rms_ref:.6f}")
    print(f"  RMS (out): {rms_out:.6f}")
    print(f"  RMS ratio: {rms_out/rms_ref:.4f}")
    print(f"  Correlation: {correlation:.6f}")
    print(f"  Normalized correlation: {normalized_correlation:.6f}")
    print(f"  Similarity: {similarity:.2f}%")
    
    return similarity

print("详细分析失败的测试:")
print("=" * 70)

failed = ["0.1058", "0.1496", "0.2007"]
passed = ["0.0547", "0.2518", "0.3102"]

print("\n失败的测试:")
for case in failed:
    analyze_similarity(case)

print("\n\n通过的测试 (作为对比):")
for case in passed:
    analyze_similarity(case)
