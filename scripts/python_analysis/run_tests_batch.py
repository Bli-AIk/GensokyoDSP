#!/usr/bin/env python3
"""
批量运行测试并分析结果
"""
import subprocess
import re
import sys
import time
from pathlib import Path

def run_single_test(test_name, timeout=60):
    """运行单个测试"""
    cmd = ["cargo", "test", "--quiet", test_name]
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd="/home/aik/rustProjects/GensokyoDSP",
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        # 检查是否通过
        passed = result.returncode == 0 and "test result: ok" in result.stdout
        
        return {
            "name": test_name,
            "passed": passed,
            "elapsed": elapsed,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return {
            "name": test_name,
            "passed": False,
            "elapsed": elapsed,
            "stdout": "",
            "stderr": f"TIMEOUT after {timeout}s"
        }

def get_all_test_names():
    """获取所有测试名称"""
    cmd = ["cargo", "test", "--", "--list"]
    result = subprocess.run(
        cmd,
        cwd="/home/aik/rustProjects/GensokyoDSP",
        capture_output=True,
        text=True
    )
    
    tests = []
    for line in result.stdout.split('\n'):
        if ': test' in line:
            test_name = line.split(':')[0].strip()
            if test_name:
                tests.append(test_name)
    
    return tests

def main():
    print("获取测试列表...")
    tests = get_all_test_names()
    print(f"找到 {len(tests)} 个测试")
    
    # 按类别分组
    categories = {}
    for test in tests:
        if test.startswith("test_vol_atk"):
            cat = "vol_atk"
        elif test.startswith("test_vol_dcy"):
            cat = "vol_dcy"
        elif test.startswith("test_vol_sus"):
            cat = "vol_sus"
        elif test.startswith("test_vol_fade"):
            cat = "vol_fade"
        elif test.startswith("test_a_form"):
            cat = "a_form"
        elif test.startswith("test_a_noise"):
            cat = "a_noise"
        elif test.startswith("test_a_color"):
            cat = "a_color"
        elif test.startswith("test_a_freq"):
            cat = "a_freq"
        elif test.startswith("test_b_form"):
            cat = "b_form"
        elif test.startswith("test_b_freq"):
            cat = "b_freq"
        elif test.startswith("test_osc_mix"):
            cat = "osc_mix"
        elif test.startswith("test_envelope"):
            cat = "envelope"
        else:
            cat = "other"
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(test)
    
    print("\n测试分布:")
    for cat, tests_list in sorted(categories.items()):
        print(f"  {cat}: {len(tests_list)} 个测试")
    
    # 运行每个类别的第一个测试作为快速检查
    print("\n运行快速检查（每个类别第一个测试）...")
    results = []
    for cat, tests_list in sorted(categories.items()):
        if tests_list:
            test = tests_list[0]
            print(f"\n运行 {cat} 类别测试: {test}")
            result = run_single_test(test, timeout=90)
            results.append(result)
            
            if result["passed"]:
                print(f"  ✓ 通过 ({result['elapsed']:.1f}s)")
            else:
                print(f"  ✗ 失败 ({result['elapsed']:.1f}s)")
                if result["stderr"]:
                    print(f"    错误: {result['stderr'][:200]}")
    
    # 总结
    print("\n" + "="*60)
    print("快速检查总结:")
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"平均耗时: {sum(r['elapsed'] for r in results) / total:.1f}s")
    
    # 显示失败的测试
    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"\n失败的测试 ({len(failed)}):")
        for r in failed:
            print(f"  - {r['name']} ({r['elapsed']:.1f}s)")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
