#!/usr/bin/env python3
"""
计算精确的b_freq频率补偿值
基于失败测试的RMS比率
"""

import numpy as np

# 失败测试的数据（从analyze_b_freq_failures.py的输出）
failing_tests = [
    {'b_freq': 0.4958, 'rms_ratio': 1.4039, 'freq': 514.1483},  # 需要降低
    {'b_freq': 0.5506, 'rms_ratio': 0.8436, 'freq': 645.8984},  # 需要提高
    {'b_freq': 0.6519, 'rms_ratio': 0.8848, 'freq': 984.1547},  # 需要提高
    {'b_freq': 0.8080, 'rms_ratio': 0.9427, 'freq': 1883.8349}, # 需要提高
    {'b_freq': 0.8502, 'rms_ratio': 0.9370, 'freq': 2245.1954}, # 需要提高
    {'b_freq': 0.9051, 'rms_ratio': 0.9052, 'freq': 2820.5016}, # 需要提高
]

# 计算需要的补偿因子（当前补偿 * 目标补偿）
print("=" * 80)
print("失败测试的频率补偿计算")
print("=" * 80)

print("\n当前RMS比率和需要的调整:")
for test in failing_tests:
    b_freq = test['b_freq']
    freq = test['freq']
    current_ratio = test['rms_ratio']
    
    # 理想情况下，我们希望RMS比率接近1.0
    # 需要的补偿调整 = 1 / current_ratio
    needed_adjustment = 1.0 / current_ratio
    
    print(f"\nb_freq={b_freq:.4f} (freq={freq:.2f}Hz):")
    print(f"  当前RMS比率: {current_ratio:.4f}")
    print(f"  需要的调整因子: {needed_adjustment:.4f}")
    print(f"  如果当前补偿是X，新补偿应该是: X * {needed_adjustment:.4f}")

# 从代码中提取的现有补偿值
print("\n" + "=" * 80)
print("代码中的现有频率补偿映射:")
print("=" * 80)

# 根据synthesizer.rs中的代码
existing_compensation = [
    # (freq_range_start, freq_range_end, comp_start, comp_end)
    (40.0, 100.0, 1.18, 1.20),         # < 100Hz
    (65.4, 130.5, 1.2162, 0.7874),     # 100-200Hz
    (130.5, 308.15, 0.7874, 0.8656),   # 200-400Hz
    (308.15, 523.0, 0.8656, 1.0),      # 400-1500Hz
    (523.0, 2093.0, 1.0, 1.1175),      # 1500-3000Hz
    (2093.0, 3754.3, 1.1175, 1.3254),  # 3000-4500Hz
    (3754.3, 5569.6, 1.3254, 1.5638),  # 4500-6500Hz
]

def get_current_compensation(freq):
    """根据当前代码逻辑计算补偿值"""
    if freq < 100.0:
        t = (freq - 40.0) / (100.0 - 40.0)
        return 1.18 + t * (1.20 - 1.18)
    elif freq < 200.0:
        t = (freq - 65.4) / (130.5 - 65.4)
        return 1.2162 + t * (0.7874 - 1.2162)
    elif freq < 400.0:
        t = (freq - 130.5) / (308.15 - 130.5)
        return 0.7874 + t * (0.8656 - 0.7874)
    elif freq < 1500.0:
        t = (freq - 308.15) / (523.0 - 308.15)
        return 0.8656 + t * (1.0 - 0.8656)
    elif freq < 3000.0:
        t = (freq - 523.0) / (2093.0 - 523.0)
        return 1.0 + t * (1.1175 - 1.0)
    elif freq < 4500.0:
        t = (freq - 2093.0) / (3754.3 - 2093.0)
        return 1.1175 + t * (1.3254 - 1.1175)
    elif freq < 6500.0:
        t = (freq - 3754.3) / (5569.6 - 3754.3)
        return 1.3254 + t * (1.5638 - 1.3254)
    else:
        base = 1.5638
        return base + ((freq - 5569.6) / 5000.0) * 0.2

print("\n对每个失败测试的分析:")
for test in failing_tests:
    freq = test['freq']
    current_comp = get_current_compensation(freq)
    rms_ratio = test['rms_ratio']
    needed_adjustment = 1.0 / rms_ratio
    new_comp = current_comp * needed_adjustment
    
    print(f"\nfreq={freq:.2f}Hz (b_freq={test['b_freq']:.4f}):")
    print(f"  当前补偿: {current_comp:.4f}")
    print(f"  RMS比率: {rms_ratio:.4f}")
    print(f"  需要的新补偿: {new_comp:.4f}")

# 生成建议的新的校准数据点
print("\n" + "=" * 80)
print("建议的新校准数据点（用于更新代码）:")
print("=" * 80)

calibration_points = []
for test in failing_tests:
    freq = test['freq']
    current_comp = get_current_compensation(freq)
    needed_adjustment = 1.0 / test['rms_ratio']
    new_comp = current_comp * needed_adjustment
    calibration_points.append((freq, new_comp))
    print(f"({freq:.2f}Hz, {new_comp:.4f})")

print("\n" + "=" * 80)
print("Rust代码更新建议:")
print("=" * 80)
print("""
基于以上分析，需要更新 synthesizer.rs 中的 freq_compensation 逻辑。
建议添加以下校准点:

514.1483Hz: {:.4f}
645.8984Hz: {:.4f}
984.1547Hz: {:.4f}
1883.8349Hz: {:.4f}
2245.1954Hz: {:.4f}
2820.5016Hz: {:.4f}
""".format(
    calibration_points[0][1],
    calibration_points[1][1],
    calibration_points[2][1],
    calibration_points[3][1],
    calibration_points[4][1],
    calibration_points[5][1],
))
