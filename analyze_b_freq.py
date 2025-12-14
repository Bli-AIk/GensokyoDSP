import numpy as np

# 已知信息
a_freq_param = 0.5
b_freq_param = 0.6875

# 当前的频率计算方式（与振荡器A相同）
def calc_freq_method1(param):
    midi = 72.0 + (param - 0.5) * 48.0
    return 440.0 * 2**((midi - 69.0) / 12.0)

freq_a = calc_freq_method1(a_freq_param)
print(f"振荡器A频率: {freq_a:.2f} Hz")

# 如果B使用相同的绝对映射
freq_b_absolute = calc_freq_method1(b_freq_param)
print(f"振荡器B频率（绝对映射）: {freq_b_absolute:.2f} Hz")
print(f"  比率: {freq_b_absolute/freq_a:.4f}")

# 如果B是相对于A的偏移（以半音为单位）
# b_freq可能表示相对音高偏移
semitones_offset = (b_freq_param - 0.5) * 48.0
freq_b_relative = freq_a * 2**(semitones_offset / 12.0)
print(f"\n振荡器B频率（相对A的半音偏移={semitones_offset:.1f}）: {freq_b_relative:.2f} Hz")
print(f"  比率: {freq_b_relative/freq_a:.4f}")

# 根据观察到的谐波，基频仍然是523Hz
# 让我们考虑另一种可能：b_freq可能控制相对倍数
print("\n观察到的谐波:")
print("  523 Hz (基频)")
print("  1047 Hz (2倍)")
print("  1570 Hz (3倍)")
print("\n这表明振荡器B可能与振荡器A频率相同，但使用不同波形（锯齿波）")

# 或者b_freq可能有其他映射方式
# 让我们看看0.6875对应的其他可能性
print("\n其他可能的映射:")

# 线性映射到倍数
multiplier = 0.5 + b_freq_param  # 0.5 + 0.6875 = 1.1875
print(f"  作为倍数（0.5+b_freq）: {freq_a * multiplier:.2f} Hz")

# 八度+微调
octave_mult = 1.0 + b_freq_param  # 1.6875
print(f"  作为倍数（1+b_freq）: {freq_a * octave_mult:.2f} Hz")

# 检查523Hz可能对应的锯齿波是什么
print("\n如果振荡器B也是523Hz但波形不同:")
print("  锯齿波会产生所有整数倍谐波: 523, 1046, 1569, 2092... Hz")
print("  这与观察到的频谱一致！")

print("\n结论: 振荡器B可能与振荡器A有相同或相近的基频，")
print("但b_freq参数可能控制:")
print("  1. 相对音高的细微调整")
print("  2. 或者在这个测试中没有明显效果")
print("  3. 主要差别是b_form=0.5（锯齿波）vs a_form=0.0（正弦波）")
