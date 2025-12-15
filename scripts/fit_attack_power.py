#!/usr/bin/env python3
"""拟合参考音频的 attack 曲线形状"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.optimize import curve_fit

def power_curve(t, power):
    """Power law curve: t^power"""
    return t ** power

cases = [("0.0547", 0.096), ("0.1058", 0.317), ("0.1496", 0.489), 
         ("0.2007", 0.381), ("0.2518", 0.265), ("0.3102", 0.155)]

fig, axes = plt.subplots(3, 2, figsize=(14, 12))
axes = axes.flatten()

print("拟合参考音频的 attack power:")
print("=" * 70)

for idx, (case, peak_time) in enumerate(cases):
    ref_file = f"tests/fixtures/vol_sus_tests/vol_sus_{case}.wav"
    
    ref_rate, ref_data = wavfile.read(ref_file)
    
    # 转换为浮点数
    if ref_data.dtype == np.int16:
        ref_data = ref_data.astype(np.float32) / 32768.0
    
    # 创建细粒度包络
    window_size = 128
    ref_env = np.array([np.sqrt(np.mean(ref_data[max(0,i-window_size//2):min(len(ref_data),i+window_size//2)]**2)) 
                        for i in range(0, len(ref_data), window_size//8)])
    
    env_time = np.arange(len(ref_env)) * (window_size/8) / ref_rate
    
    # 找到峰值
    peak_idx = np.argmax(ref_env)
    actual_peak_time = env_time[peak_idx]
    peak_val = ref_env[peak_idx]
    
    # 提取 attack 段 (从0到峰值)
    attack_mask = env_time <= actual_peak_time
    attack_time = env_time[attack_mask]
    attack_env = ref_env[attack_mask]
    
    # 归一化时间 [0, 1] 和幅度 [0, 1]
    if len(attack_time) > 10:
        t_norm = attack_time / actual_peak_time
        env_norm = attack_env / peak_val
        
        # 拟合 power 曲线
        try:
            # 过滤掉开头的噪声
            valid_mask = (t_norm > 0.01) & (env_norm > 0.01)
            t_fit = t_norm[valid_mask]
            env_fit = env_norm[valid_mask]
            
            if len(t_fit) > 5:
                popt, _ = curve_fit(power_curve, t_fit, env_fit, p0=[1.0], bounds=([0.1], [10.0]))
                fitted_power = popt[0]
                
                # 生成拟合曲线
                t_dense = np.linspace(0, 1, 100)
                fitted_curve = power_curve(t_dense, fitted_power)
                
                # 绘图
                axes[idx].plot(t_norm, env_norm, 'b-', label='Reference', linewidth=2)
                axes[idx].plot(t_dense, fitted_curve, 'r--', label=f'Fitted (power={fitted_power:.3f})', linewidth=2)
                axes[idx].plot(t_dense, power_curve(t_dense, 0.93), 'g:', label='Current (power=0.93)', linewidth=1.5)
                axes[idx].set_xlabel('Normalized Time')
                axes[idx].set_ylabel('Normalized Amplitude')
                axes[idx].set_title(f'vol_sus_{case} - Attack Curve')
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
                
                print(f"vol_sus_{case}: peak_time={actual_peak_time:.3f}s, fitted_power={fitted_power:.3f}")
            else:
                print(f"vol_sus_{case}: 不足数据点")
        except Exception as e:
            print(f"vol_sus_{case}: 拟合失败 - {e}")

plt.tight_layout()
plt.savefig('attack_power_fitting.png', dpi=150)
print(f"\n图表已保存到 attack_power_fitting.png")
