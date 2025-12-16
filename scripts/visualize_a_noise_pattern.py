#!/usr/bin/env python3
"""可视化a_noise对attack时间的影响"""

import numpy as np
import matplotlib.pyplot as plt

# 从参考文件测得的数据
data = [
    (0.0547, 0.4250),
    (0.1058, 0.3500),
    (0.1496, 4.1150),
    (0.2007, 0.3950),
    (0.2518, 4.9900),
    (0.3102, 0.1950),
    (0.4051, 3.8650),
    (0.4536, 7.0000),
    (0.4958, 0.0350),
    (0.5506, 0.0550),
    (0.6055, 0.1400),
    (0.6519, 3.3300),
    (0.7025, 0.3050),
    (0.7489, 0.3650),
    (0.8502, 2.0450),
    (0.9051, 2.0050),
    (0.9515, 3.9850),
    (1.0000, 0.4400),
]

a_noise_vals = [d[0] for d in data]
attack_times = [d[1] for d in data]

# 创建图表
plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
plt.scatter(a_noise_vals, attack_times, s=100, alpha=0.7, c='blue')
for i, (x, y) in enumerate(data):
    plt.text(x, y + 0.2, f'{x:.4f}', ha='center', fontsize=8)
plt.xlabel('a_noise')
plt.ylabel('Attack Time (s)')
plt.title('a_noise vs Attack Time (All Points)')
plt.grid(True, alpha=0.3)

# 高亮高噪声组
plt.subplot(1, 2, 2)
high_noise = [(x, y) for x, y in data if x >= 0.8]
hn_x = [d[0] for d in high_noise]
hn_y = [d[1] for d in high_noise]

plt.scatter(hn_x, hn_y, s=150, alpha=0.7, c='red')
for x, y in high_noise:
    plt.text(x, y + 0.1, f'{x:.4f}\\n{y:.2f}s', ha='center', fontsize=10)
plt.xlabel('a_noise')
plt.ylabel('Attack Time (s)')
plt.title('High Noise Group (a_noise >= 0.8)')
plt.grid(True, alpha=0.3)
plt.xlim(0.79, 1.01)

plt.tight_layout()
plt.savefig('temps/a_noise_attack_pattern.png', dpi=150)
print('图表已保存到 temps/a_noise_attack_pattern.png')

# 尝试找到模式
print('\\n高噪声组attack时间:')
print('-' * 40)
for x, y in high_noise:
    print(f'  a_noise={x:.4f}: attack={y:.4f}s')

# 检查是否与随机种子有关
print('\\n可能的解释:')
print('1. a_noise可能影响调制包络(mod envelope)')
print('2. a_noise可能触发不同的包络行为模式')
print('3. attack时间可能由某种非线性函数控制')
print('')
print('关键观察:')
print(f'  a_noise=0.8502: attack=2.045s (中等)')
print(f'  a_noise=0.9051: attack=2.005s (中等)')
print(f'  a_noise=0.9515: attack=3.985s (慢)')
print(f'  a_noise=1.0000: attack=0.440s (快!)')
