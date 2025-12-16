#!/usr/bin/env python3
"""
计算高频b_freq测试所需的额外增益补偿
"""
import numpy as np

# 参考RMS值（目标值）
reference_rms = {
    0.4958: 0.049251,
    0.5506: 0.054026,
    0.6519: 0.055801,
    0.8080: 0.056978,
    0.8502: 0.056594,
    0.9051: 0.057480,
}

# 测试输出RMS值（当前值）
test_rms = {
    0.4958: 0.058182,
    0.5506: 0.057881,
    0.6519: 0.057042,
    0.8080: 0.048066,
    0.8502: 0.040010,
    0.9051: 0.033273,
}

# 对应的频率
frequencies = {
    0.4958: 65.39,
    0.5506: 130.50,
    0.6519: 308.15,
    0.8080: 2092.92,
    0.8502: 3754.31,
    0.9051: 5569.57,
}

print("=" * 80)
print("b_freq测试RMS补偿分析")
print("=" * 80)

for b_freq_param in sorted(reference_rms.keys()):
    ref = reference_rms[b_freq_param]
    test = test_rms[b_freq_param]
    freq = frequencies[b_freq_param]
    
    needed_gain = ref / test
    current_error = (test - ref) / ref * 100
    
    print(f"\nb_freq = {b_freq_param:.4f} ({freq:.2f} Hz)")
    print(f"  参考RMS: {ref:.6f}")
    print(f"  测试RMS: {test:.6f}")
    print(f"  误差: {current_error:+.2f}%")
    print(f"  需要增益: {needed_gain:.4f}x")

print("\n" + "=" * 80)
print("频率依赖补偿建议")
print("=" * 80)

# 寻找频率依赖模式
print("\n观察：")
print("- 低频 (<500Hz): 测试RMS过高 (+7% to +18%)")
print("- 中频 (500-1000Hz): 测试RMS接近目标 (+2%)")
print("- 高频 (>2000Hz): 测试RMS严重偏低 (-15% to -42%)")
print("\n建议：在synthesizer.rs中为高频振荡器B添加频率依赖的增益补偿")

# 计算频率依赖的补偿因子
print("\n补偿因子（相对于无补偿）:")
for b_freq_param in sorted(reference_rms.keys()):
    freq = frequencies[b_freq_param]
    gain = reference_rms[b_freq_param] / test_rms[b_freq_param]
    
    # 相对于中频基准（0.6519）的额外补偿
    baseline_gain = reference_rms[0.6519] / test_rms[0.6519]
    extra_gain = gain / baseline_gain
    
    print(f"  {freq:7.2f} Hz: {extra_gain:.4f}x (总增益: {gain:.4f}x)")
