#!/usr/bin/env python3
"""
分析失败的单元测试，提取音频差异信息
"""

import subprocess
import re
import json
from pathlib import Path

def run_tests_and_extract_failures():
    """运行测试并提取失败信息"""
    print("运行测试并收集失败信息...")
    
    result = subprocess.run(
        ["cargo", "test", "--test", "synthesis_tests", "--", "--nocapture"],
        cwd="/workspaces/GensokyoDSP",
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    
    # 提取失败的测试及其详细信息
    failures = []
    
    # 匹配模式：测试名称和相似度信息
    pattern = r"测试 '([^']+)' 结果:.*?相似度: ([\d.]+)%.*?测试失败: \"相似度 [\d.]+% 低于阈值 ([\d.]+)%\""
    
    matches = re.finditer(pattern, output, re.DOTALL)
    
    for match in matches:
        test_name = match.group(1)
        similarity = float(match.group(2))
        threshold = float(match.group(3))
        
        # 提取参数名和值
        parts = test_name.split('_')
        if len(parts) >= 2:
            param_name = parts[0]
            param_value = parts[1]
            
            failures.append({
                'test_name': test_name,
                'param_name': param_name,
                'param_value': param_value,
                'similarity': similarity,
                'threshold': threshold,
                'gap': threshold - similarity
            })
    
    return failures

def analyze_patterns(failures):
    """分析失败模式"""
    print("\n=== 失败测试分析 ===\n")
    
    # 按参数分组
    by_param = {}
    for f in failures:
        param = f['param_name']
        if param not in by_param:
            by_param[param] = []
        by_param[param].append(f)
    
    for param, tests in sorted(by_param.items()):
        print(f"\n参数: {param}")
        print(f"失败数量: {len(tests)}")
        
        # 排序并显示
        tests_sorted = sorted(tests, key=lambda x: float(x['param_value']))
        
        print(f"{'值':<10} {'相似度':<10} {'差距':<10}")
        print("-" * 30)
        for t in tests_sorted:
            print(f"{t['param_value']:<10} {t['similarity']:<10.2f} {t['gap']:<10.2f}")
        
        # 统计信息
        similarities = [t['similarity'] for t in tests]
        gaps = [t['gap'] for t in tests]
        
        print(f"\n统计:")
        print(f"  平均相似度: {sum(similarities)/len(similarities):.2f}%")
        print(f"  平均差距: {sum(gaps)/len(gaps):.2f}%")
        print(f"  最小相似度: {min(similarities):.2f}%")
        print(f"  最大相似度: {max(similarities):.2f}%")

def main():
    failures = run_tests_and_extract_failures()
    
    if not failures:
        print("所有测试通过！")
        return
    
    print(f"\n发现 {len(failures)} 个失败的测试\n")
    
    analyze_patterns(failures)
    
    # 保存到JSON文件
    output_file = Path("/workspaces/GensokyoDSP/scripts/analysis/test_failures.json")
    with open(output_file, 'w') as f:
        json.dump(failures, f, indent=2)
    
    print(f"\n\n详细信息已保存到: {output_file}")

if __name__ == "__main__":
    main()
