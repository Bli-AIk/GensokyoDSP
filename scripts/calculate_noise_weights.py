#!/usr/bin/env python3
"""计算当前实现的预期RMS"""
import numpy as np

def predict_rms(a_noise, base_osc_rms=0.055638):
    """预测当前实现生成的RMS"""
    
    if a_noise < 0.8:
        # 只有振荡器
        osc_weight = 1.0
        noise_weight = 0.0
    else:
        # 混合模式
        t = (a_noise - 0.8) / 0.2
        osc_weight = 1.0 - t
        noise_weight = t * 0.118
    
    # 假设噪声RMS与振荡器RMS相当（这是个假设）
    # 在能量叠加模式下: RMS^2_total = RMS^2_osc * w_osc^2 + RMS^2_noise * w_noise^2
    # 简化假设: 噪声RMS = 振荡器RMS
    predicted_rms = base_osc_rms * np.sqrt(osc_weight**2 + noise_weight**2)
    
    return predicted_rms, osc_weight, noise_weight

# 测试失败的值
test_values = [0.8502, 0.9051, 0.9515, 1.0]
reference_rms = {
    0.8502: 0.051202,
    0.9051: 0.045150,
    0.9515: 0.042051,
    1.0: 0.042440
}

print("=" * 80)
print("当前实现的RMS预测 vs 参考RMS")
print("=" * 80)
print(f"{'a_noise':>10s} {'Ref RMS':>12s} {'Pred RMS':>12s} {'差异':>12s} {'Osc W':>10s} {'Noise W':>10s}")
print("-" * 80)

for val in test_values:
    pred_rms, osc_w, noise_w = predict_rms(val)
    ref_rms = reference_rms[val]
    diff = pred_rms - ref_rms
    print(f"{val:>10.4f} {ref_rms:>12.6f} {pred_rms:>12.6f} {diff:>12.6f} {osc_w:>10.4f} {noise_w:>10.4f}")

print("\n" + "=" * 80)
print("分析: 预测RMS都比参考RMS高，说明我们的能量太多")
print("=" * 80)

# 计算需要的总增益系数
print("\n需要的调整:")
for val in test_values:
    ref_rms = reference_rms[val]
    pred_rms, osc_w, noise_w = predict_rms(val)
    needed_gain = ref_rms / pred_rms
    print(f"  a_noise={val:.4f}: 需要整体增益 {needed_gain:.4f}")

# 尝试反推正确的权重
print("\n" + "=" * 80)
print("反推正确的权重配置")
print("=" * 80)

base_rms = 0.055638

for val in test_values:
    ref_rms = reference_rms[val]
    t = (val - 0.8) / 0.2
    
    # 假设：总RMS^2 = (osc_weight * base_rms)^2 + (noise_weight * noise_rms)^2
    # 并且noise_rms = k * base_rms （假设噪声RMS是振荡器RMS的k倍）
    # 则: ref_rms^2 = base_rms^2 * (osc_weight^2 + noise_weight^2 * k^2)
    
    # 如果我们保持osc_weight = 1.0 - t
    osc_weight = 1.0 - t
    
    # 那么: (ref_rms / base_rms)^2 = osc_weight^2 + noise_weight^2 * k^2
    # 如果假设k=1 (噪声和振荡器RMS相同):
    rms_ratio_sq = (ref_rms / base_rms) ** 2
    noise_weight_sq = rms_ratio_sq - osc_weight**2
    
    if noise_weight_sq >= 0:
        noise_weight = np.sqrt(noise_weight_sq)
        print(f"  a_noise={val:.4f} (t={t:.3f}): osc_w={osc_weight:.4f}, noise_w={noise_weight:.4f}")
    else:
        # RMS下降太多，单靠减少osc_weight不够
        # 需要整体缩放
        overall_gain = ref_rms / (base_rms * osc_weight)
        print(f"  a_noise={val:.4f} (t={t:.3f}): 需要整体增益 {overall_gain:.4f}, noise_w=0")

# 另一种方法：固定noise_weight，调整整体增益
print("\n" + "=" * 80)
print("方案2: 保持当前权重公式，添加整体增益调整")
print("=" * 80)

for val in test_values:
    ref_rms = reference_rms[val]
    t = (val - 0.8) / 0.2
    osc_weight = 1.0 - t
    noise_weight = t * 0.118
    
    current_rms = base_rms * np.sqrt(osc_weight**2 + noise_weight**2)
    needed_gain = ref_rms / current_rms
    
    print(f"  a_noise={val:.4f}: 整体增益 {needed_gain:.4f}")

# 拟合增益曲线
print("\n尝试拟合增益曲线为 a_noise 的函数:")
gains = []
a_noise_vals = []
for val in test_values:
    ref_rms = reference_rms[val]
    t = (val - 0.8) / 0.2
    osc_weight = 1.0 - t
    noise_weight = t * 0.118
    current_rms = base_rms * np.sqrt(osc_weight**2 + noise_weight**2)
    needed_gain = ref_rms / current_rms
    gains.append(needed_gain)
    a_noise_vals.append(val)

# 线性拟合
gains = np.array(gains)
a_noise_vals = np.array(a_noise_vals)
p = np.polyfit(a_noise_vals, gains, 1)
print(f"线性拟合: gain = {p[0]:.4f} * a_noise + {p[1]:.4f}")

# 验证拟合
print("\n验证拟合效果:")
for val in test_values:
    predicted_gain = p[0] * val + p[1]
    t = (val - 0.8) / 0.2
    osc_weight = 1.0 - t
    noise_weight = t * 0.118
    predicted_rms = base_rms * np.sqrt(osc_weight**2 + noise_weight**2) * predicted_gain
    ref_rms = reference_rms[val]
    error = abs(predicted_rms - ref_rms)
    print(f"  a_noise={val:.4f}: pred={predicted_rms:.6f}, ref={ref_rms:.6f}, error={error:.6f}")
