#!/usr/bin/env python3
"""计算需要的rolloff调整以匹配谐波比率"""

import math

# 当前rolloff公式: rolloff_factor = 1.0 / (1.0 + (n / rolloff_strength)^2)
# 对于form=0.5, 使用generate_saw时:
# saw_rolloff = 5000.0 / freq

def calc_rolloff_factor(n, rolloff_strength):
    """计算当前的rolloff因子"""
    return 1.0 / (1.0 + (n / rolloff_strength)**2)

def find_needed_rolloff(n, current_rolloff, target_ratio, current_ratio):
    """
    找到需要的rolloff使得谐波比率达到目标
    current_ratio = 测试幅度 / 参考幅度
    target_ratio = 1.0 (完美匹配)
    """
    # 当前衰减因子
    current_factor = calc_rolloff_factor(n, current_rolloff)
    
    # 需要的提升倍数
    boost_needed = target_ratio / current_ratio
    
    # 需要的rolloff因子
    needed_factor = current_factor * boost_needed
    
    # 反推rolloff_strength
    if needed_factor >= 1.0:
        return float('inf')  # 无衰减
    
    # 1 / (1 + (n/r)^2) = needed_factor
    # 1 + (n/r)^2 = 1 / needed_factor
    # (n/r)^2 = 1/needed_factor - 1
    # r = n / sqrt(1/needed_factor - 1)
    
    if needed_factor <= 0:
        return 0
    
    divisor = 1.0/needed_factor - 1.0
    if divisor <= 0:
        return float('inf')
    
    needed_rolloff = n / math.sqrt(divisor)
    return needed_rolloff

# 分析每个失败案例
cases = [
    (65.0, 0.4958, [
        (2, 0.5281),
        (3, 0.6653),
        (4, 0.6391),
        (5, 0.5910),
        (6, 0.5268),
        (7, 0.4919),
    ]),
    (130.0, 0.5506, [
        (2, 0.6595),
        (3, 0.7298),
        (4, 0.8140),
    ]),
    (308.0, 0.6519, [
        (2, 0.5818),
        (3, 0.6788),
        (5, 0.4882),
    ]),
]

print("="*80)
print("分析谐波rolloff需求")
print("="*80)

for freq, param, harmonics in cases:
    current_rolloff = 5000.0 / freq
    print(f"\nb_freq={param} ({freq} Hz)")
    print(f"当前rolloff_strength: {current_rolloff:.1f}")
    print(f"\n谐波分析:")
    print(f"{'谐波':<6} {'当前比率':<10} {'当前因子':<12} {'需要因子':<12} {'需要rolloff':<15}")
    print("-" * 70)
    
    suggested_rolloffs = []
    for n, ratio in harmonics:
        current_factor = calc_rolloff_factor(n, current_rolloff)
        needed_rolloff = find_needed_rolloff(n, current_rolloff, 1.0, ratio)
        needed_factor = calc_rolloff_factor(n, needed_rolloff) if needed_rolloff < float('inf') else 1.0
        
        print(f"{n:<6} {ratio:<10.4f} {current_factor:<12.4f} {needed_factor:<12.4f} {needed_rolloff:<15.1f}")
        
        if needed_rolloff < float('inf'):
            suggested_rolloffs.append(needed_rolloff)
    
    if suggested_rolloffs:
        avg_suggested = sum(suggested_rolloffs) / len(suggested_rolloffs)
        print(f"\n建议rolloff: {avg_suggested:.1f} (当前: {current_rolloff:.1f}, 提升: {avg_suggested/current_rolloff:.2f}x)")
