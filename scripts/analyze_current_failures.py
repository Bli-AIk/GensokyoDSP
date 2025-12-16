#!/usr/bin/env python3
"""分析当前失败的测试用例"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.io.wavfile as wavfile
from scipy import signal
import json

# 失败的测试用例
FAILED_TESTS = {
    'a_noise': [0.8502, 0.9051, 0.9515, 1.0],
    'b_freq': [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051]
}

def load_wav(filepath):
    """加载WAV文件"""
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]  # 只取第一个声道
    return rate, data.astype(np.float32) / 32768.0

def compute_spectral_centroid(data, rate):
    """计算频谱质心"""
    # 计算频谱
    f, t, Sxx = signal.spectrogram(data, rate, nperseg=1024)
    # 计算质心
    centroid = np.sum(f[:, np.newaxis] * Sxx, axis=0) / (np.sum(Sxx, axis=0) + 1e-10)
    return np.mean(centroid)

def compute_envelope(data, rate):
    """计算包络"""
    # 使用Hilbert变换
    analytic_signal = signal.hilbert(data)
    amplitude_envelope = np.abs(analytic_signal)
    return amplitude_envelope

def analyze_time_domain(ref_data, gen_data, rate):
    """时域分析"""
    results = {}
    
    # RMS比较
    ref_rms = np.sqrt(np.mean(ref_data**2))
    gen_rms = np.sqrt(np.mean(gen_data**2))
    results['ref_rms'] = ref_rms
    results['gen_rms'] = gen_rms
    results['rms_ratio'] = gen_rms / (ref_rms + 1e-10)
    
    # 峰值比较
    results['ref_peak'] = np.max(np.abs(ref_data))
    results['gen_peak'] = np.max(np.abs(gen_data))
    
    # 包络分析
    ref_env = compute_envelope(ref_data, rate)
    gen_env = compute_envelope(gen_data, rate)
    
    # 包络相似度
    env_corr = np.corrcoef(ref_env[:min(len(ref_env), len(gen_env))], 
                            gen_env[:min(len(ref_env), len(gen_env))])[0, 1]
    results['envelope_correlation'] = env_corr
    
    return results

def analyze_frequency_domain(ref_data, gen_data, rate):
    """频域分析"""
    results = {}
    
    # FFT
    ref_fft = np.fft.rfft(ref_data)
    gen_fft = np.fft.rfft(gen_data)
    
    ref_mag = np.abs(ref_fft)
    gen_mag = np.abs(gen_fft)
    
    # 频谱相似度
    spec_corr = np.corrcoef(ref_mag[:min(len(ref_mag), len(gen_mag))],
                             gen_mag[:min(len(ref_mag), len(gen_mag))])[0, 1]
    results['spectrum_correlation'] = spec_corr
    
    # 频谱质心
    results['ref_centroid'] = compute_spectral_centroid(ref_data, rate)
    results['gen_centroid'] = compute_spectral_centroid(gen_data, rate)
    
    return results

def analyze_test(param_name, param_value):
    """分析单个测试"""
    # 文件路径
    ref_file = Path(f"tests/fixtures/{param_name}_tests/{param_name}_{param_value}.wav")
    gen_file = Path(f"tests/output/test_{param_name}_{param_value}.wav")
    
    if not ref_file.exists():
        print(f"  ✗ 参考文件不存在: {ref_file}")
        return None
    
    if not gen_file.exists():
        print(f"  ✗ 生成文件不存在: {gen_file}")
        return None
    
    # 加载音频
    ref_rate, ref_data = load_wav(ref_file)
    gen_rate, gen_data = load_wav(gen_file)
    
    if ref_rate != gen_rate:
        print(f"  ✗ 采样率不匹配: {ref_rate} vs {gen_rate}")
        return None
    
    # 确保长度一致
    min_len = min(len(ref_data), len(gen_data))
    ref_data = ref_data[:min_len]
    gen_data = gen_data[:min_len]
    
    # 分析
    time_results = analyze_time_domain(ref_data, gen_data, ref_rate)
    freq_results = analyze_frequency_domain(ref_data, gen_data, ref_rate)
    
    results = {**time_results, **freq_results}
    
    # 计算总体相似度（基于多个指标）
    similarity_scores = []
    
    # RMS相似度
    rms_sim = 1.0 - min(abs(results['rms_ratio'] - 1.0), 1.0)
    similarity_scores.append(rms_sim * 100)
    
    # 包络相似度
    if not np.isnan(results['envelope_correlation']):
        similarity_scores.append(max(0, results['envelope_correlation'] * 100))
    
    # 频谱相似度
    if not np.isnan(results['spectrum_correlation']):
        similarity_scores.append(max(0, results['spectrum_correlation'] * 100))
    
    results['overall_similarity'] = np.mean(similarity_scores) if similarity_scores else 0
    
    return results

def print_results(param_name, param_value, results):
    """打印分析结果"""
    if results is None:
        return
    
    print(f"\n  {param_name}={param_value}:")
    print(f"    RMS: ref={results['ref_rms']:.6f}, gen={results['gen_rms']:.6f}, ratio={results['rms_ratio']:.4f}")
    print(f"    Peak: ref={results['ref_peak']:.6f}, gen={results['gen_peak']:.6f}")
    print(f"    包络相关性: {results['envelope_correlation']:.4f}")
    print(f"    频谱相关性: {results['spectrum_correlation']:.4f}")
    print(f"    频谱质心: ref={results['ref_centroid']:.1f} Hz, gen={results['gen_centroid']:.1f} Hz")
    print(f"    总体相似度: {results['overall_similarity']:.2f}%")

def main():
    print("=" * 80)
    print("当前失败测试分析")
    print("=" * 80)
    
    for param_name, param_values in FAILED_TESTS.items():
        print(f"\n{'=' * 80}")
        print(f"参数: {param_name}")
        print('=' * 80)
        
        all_results = {}
        
        for param_value in param_values:
            results = analyze_test(param_name, param_value)
            if results:
                all_results[param_value] = results
                print_results(param_name, param_value, results)
        
        # 查找模式
        if all_results:
            print(f"\n  {param_name} 模式分析:")
            
            # RMS比率趋势
            rms_ratios = [r['rms_ratio'] for r in all_results.values()]
            print(f"    RMS比率范围: {min(rms_ratios):.4f} - {max(rms_ratios):.4f}")
            print(f"    RMS比率平均: {np.mean(rms_ratios):.4f}")
            
            # 包络相关性趋势
            env_corrs = [r['envelope_correlation'] for r in all_results.values() if not np.isnan(r['envelope_correlation'])]
            if env_corrs:
                print(f"    包络相关性范围: {min(env_corrs):.4f} - {max(env_corrs):.4f}")
                print(f"    包络相关性平均: {np.mean(env_corrs):.4f}")
            
            # 频谱相关性趋势
            spec_corrs = [r['spectrum_correlation'] for r in all_results.values() if not np.isnan(r['spectrum_correlation'])]
            if spec_corrs:
                print(f"    频谱相关性范围: {min(spec_corrs):.4f} - {max(spec_corrs):.4f}")
                print(f"    频谱相关性平均: {np.mean(spec_corrs):.4f}")

if __name__ == "__main__":
    main()
