#!/usr/bin/env python3
"""
分析所有失败的测试，提取关键信息
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import soundfile as sf
from pathlib import Path

# 失败的测试列表
FAILED_TESTS = {
    'a_noise': [0.8502, 0.9051, 0.9515, 1.0],
    'b_freq': [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051],
    'osc_mix': [0.8502],
}

def analyze_audio_file(filepath):
    """分析单个音频文件"""
    data, sr = sf.read(filepath)
    
    if len(data.shape) > 1:
        data = data[:, 0]  # 使用左声道
    
    # 基本统计
    rms = np.sqrt(np.mean(data**2))
    peak = np.max(np.abs(data))
    
    # 频谱分析
    fft = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1/sr)
    magnitude = np.abs(fft)
    
    # 找到主要频率成分
    top_indices = np.argsort(magnitude)[-10:][::-1]
    top_freqs = freqs[top_indices]
    top_mags = magnitude[top_indices]
    
    return {
        'rms': rms,
        'peak': peak,
        'duration': len(data) / sr,
        'sample_rate': sr,
        'top_freqs': top_freqs,
        'top_mags': top_mags,
    }

def compare_files(ref_path, test_path):
    """比较两个音频文件"""
    ref_data, ref_sr = sf.read(ref_path)
    test_data, test_sr = sf.read(test_path)
    
    if len(ref_data.shape) > 1:
        ref_data = ref_data[:, 0]
    if len(test_data.shape) > 1:
        test_data = test_data[:, 0]
    
    # 确保长度相同
    min_len = min(len(ref_data), len(test_data))
    ref_data = ref_data[:min_len]
    test_data = test_data[:min_len]
    
    # RMS差异
    rms_ref = np.sqrt(np.mean(ref_data**2))
    rms_test = np.sqrt(np.mean(test_data**2))
    rms_diff = abs(rms_ref - rms_test)
    
    # 相关性
    correlation = np.corrcoef(ref_data, test_data)[0, 1]
    
    # 频谱差异
    fft_ref = np.abs(np.fft.rfft(ref_data))
    fft_test = np.abs(np.fft.rfft(test_data))
    spectral_diff = np.mean(np.abs(fft_ref - fft_test))
    
    return {
        'rms_ref': rms_ref,
        'rms_test': rms_test,
        'rms_diff': rms_diff,
        'correlation': correlation,
        'spectral_diff': spectral_diff,
    }

def main():
    fixtures_dir = Path('/workspaces/GensokyoDSP/tests/fixtures')
    output_dir = Path('/workspaces/GensokyoDSP/tests/output')
    
    print("=" * 80)
    print("失败测试分析报告")
    print("=" * 80)
    
    for param_name, values in FAILED_TESTS.items():
        print(f"\n{'='*80}")
        print(f"参数: {param_name}")
        print(f"{'='*80}")
        
        for value in values:
            value_str = f"{value:.4f}"
            ref_file = fixtures_dir / f"{param_name}_tests" / f"{param_name}_{value_str}.wav"
            test_file = output_dir / f"test_{param_name}_{value_str}.wav"
            
            if not ref_file.exists():
                print(f"\n  ✗ {value:.4f}: 参考文件不存在")
                continue
            
            if not test_file.exists():
                print(f"\n  ✗ {value:.4f}: 测试文件不存在")
                continue
            
            print(f"\n  {param_name} = {value:.4f}")
            print("  " + "-" * 76)
            
            # 分析参考文件
            ref_info = analyze_audio_file(ref_file)
            print(f"  参考文件:")
            print(f"    RMS: {ref_info['rms']:.6f}")
            print(f"    峰值: {ref_info['peak']:.6f}")
            print(f"    时长: {ref_info['duration']:.3f}s")
            
            # 分析测试文件
            test_info = analyze_audio_file(test_file)
            print(f"  测试文件:")
            print(f"    RMS: {test_info['rms']:.6f}")
            print(f"    峰值: {test_info['peak']:.6f}")
            print(f"    时长: {test_info['duration']:.3f}s")
            
            # 比较
            comparison = compare_files(ref_file, test_file)
            print(f"  比较结果:")
            print(f"    RMS差异: {comparison['rms_diff']:.6f} ({comparison['rms_diff']/comparison['rms_ref']*100:.2f}%)")
            print(f"    相关性: {comparison['correlation']:.4f}")
            print(f"    频谱差异: {comparison['spectral_diff']:.2f}")
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
