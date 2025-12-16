#!/usr/bin/env python3
"""计算精确的噪声增益曲线"""
import numpy as np

# 参考RMS数据
ref_data = [
    (0.7489, 0.055806),  # 基准
    (0.8080, 0.054642),
    (0.8502, 0.051202),
    (0.9051, 0.045150),
    (0.9515, 0.042051),
    (1.0, 0.042440),
]

base_osc_rms = 0.055806

# 当前混合权重
def get_weights(a_noise):
    if a_noise < 0.8:
        return 1.0, 0.0
    t = (a_noise - 0.8) / 0.2
    osc_weight = 1.0 - t
    noise_weight = t * 0.118
    return osc_weight, noise_weight

print("=" * 80)
print("反推所需的噪声RMS")
print("=" * 80)
print(f"{'a_noise':>10s} {'t':>8s} {'osc_w':>10s} {'noise_w':>10s} {'target_RMS':>12s} {'需要noise_RMS':>15s} {'noise_gain':>12s}")
print("-" * 80)

# 假设：total_RMS^2 = (osc_w * base_osc_rms)^2 + (noise_w * noise_rms)^2
# 求解：noise_rms = sqrt((target_RMS^2 - (osc_w * base_osc_rms)^2) / noise_w^2)

noise_gains = []
for a_noise, target_rms in ref_data:
    if a_noise < 0.8:
        continue
    
    osc_w, noise_w = get_weights(a_noise)
    
    # 计算需要的噪声RMS
    osc_contribution = (osc_w * base_osc_rms) ** 2
    target_total = target_rms ** 2
    
    if noise_w > 0:
        noise_contribution_needed = target_total - osc_contribution
        if noise_contribution_needed > 0:
            noise_rms_needed = np.sqrt(noise_contribution_needed) / noise_w
            # 假设base_noise_rms约为0.05 (ColoredNoise的典型输出)
            base_noise_rms = 0.05  
            noise_gain = noise_rms_needed / base_noise_rms
        else:
            noise_rms_needed = 0
            noise_gain = 0
    else:
        noise_rms_needed = 0
        noise_gain = 0
    
    t = (a_noise - 0.8) / 0.2
    noise_gains.append((a_noise, t, noise_gain))
    
    print(f"{a_noise:>10.4f} {t:>8.3f} {osc_w:>10.4f} {noise_w:>10.4f} {target_rms:>12.6f} {noise_rms_needed:>15.6f} {noise_gain:>12.4f}")

# 拟合噪声增益曲线
print("\n" + "=" * 80)
print("拟合噪声增益曲线")
print("=" * 80)

a_noise_vals = np.array([x[0] for x in noise_gains])
t_vals = np.array([x[1] for x in noise_gains])
gain_vals = np.array([x[2] for x in noise_gains])

# 尝试不同的拟合
# 1. 线性拟合 (基于t)
p1 = np.polyfit(t_vals, gain_vals, 1)
print(f"线性拟合 (基于t): noise_gain = {p1[0]:.4f} * t + {p1[1]:.4f}")

# 2. 二次拟合
p2 = np.polyfit(t_vals, gain_vals, 2)
print(f"二次拟合 (基于t): noise_gain = {p2[0]:.4f} * t^2 + {p2[1]:.4f} * t + {p2[2]:.4f}")

# 3. 幂律拟合
# noise_gain = a * t^b
log_t = np.log(t_vals[t_vals > 0])
log_gain = np.log(gain_vals[len(gain_vals) - len(log_t):])
p3 = np.polyfit(log_t, log_gain, 1)
a_pow = np.exp(p3[1])
b_pow = p3[0]
print(f"幂律拟合: noise_gain = {a_pow:.4f} * t^{b_pow:.4f}")

# 验证拟合效果
print("\n验证二次拟合:")
for a_noise, t, actual_gain in noise_gains:
    predicted_gain = p2[0] * t**2 + p2[1] * t + p2[2]
    error_pct = abs(predicted_gain - actual_gain) / actual_gain * 100 if actual_gain > 0 else 0
    print(f"  a_noise={a_noise:.4f}, t={t:.3f}: 实际={actual_gain:.4f}, 预测={predicted_gain:.4f}, 误差={error_pct:.1f}%")
