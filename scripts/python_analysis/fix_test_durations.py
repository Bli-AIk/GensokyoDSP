#!/usr/bin/env python3
"""
修正 synthesis_tests.rs 中的 duration 值
"""
import re

def fix_durations():
    filepath = "/home/aik/rustProjects/GensokyoDSP/tests/synthesis_tests.rs"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要修改为 7.019 的测试类型
    test_types_to_fix = [
        'ANoiseTestCase',
        'AColorTestCase',
        'AFreqTestCase',
        'BFormTestCase',
        'BFreqTestCase',
        'OscMixTestCase'
    ]
    
    original_content = content
    
    # 对每种测试类型进行修改
    for test_type in test_types_to_fix:
        # 查找该测试类型的所有测试函数
        # 模式：let test = TestType { ... duration: 7.24, ... }
        pattern = rf'(let test = {test_type} \{{[^}}]*?duration: )7\.24(,)'
        replacement = r'\g<1>7.019\2'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 统计修改了多少处
        count = len(re.findall(r'duration: 7\.019,', content)) - len(re.findall(r'duration: 7\.019,', original_content))
        print(f"已修改 {count} 处 duration 值：7.24 -> 7.019")
        print("\n修改的测试类型:")
        for test_type in test_types_to_fix:
            print(f"  - {test_type}")
    else:
        print("没有需要修改的内容")

if __name__ == "__main__":
    fix_durations()
