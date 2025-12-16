#!/usr/bin/env python3
"""
分析 b_freq 测试失败的原因
根据 synplant_format_zh.md:
- b_freq 在 0.4325 之前只播放 A 波形
- b_freq 在 0.5 之后只播放 B 波形
- 0.4325 - 0.5 是过渡段
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from pathlib import Path

# 失败的测试值
failing_tests = [
    0.4958,  # 93.31%
    0.5506,  # 91.60%
    0.6519,  # 91.87%
    0.8080,  # 93.36%
    0.8502,  # 90.18%
    0.9051,  # 90.88%
]

def analyze_b_freq_value(b_freq_value):
    """分析单个 b_freq 值的音频"""
    
    # 构建文件路径
    ref_file = Path(f"tests/fixtures/b_freq_tests/b_freq_{b_freq_value:.4f}.wav")
    gen_file = Path(f"tests/output/test_b_freq_{b_freq_value:.4f}.wav")
    
    if not ref_file.exists():
        print(f"参考文件不存在: {ref_file}")
        return
    if not gen_file.exists():
        print(f"生成文件不存在: {gen_file}")
        return
    
    # 读取音频
    sr_ref, audio_ref = wavfile.read(ref_file)
    sr_gen, audio_gen = wavfile.read(gen_file)
    
    # 转换为浮点数
    if audio_ref.dtype == np.int16:
        audio_ref = audio_ref.astype(np.float32) / 32768.0
    if audio_gen.dtype == np.int16:
        audio_gen = audio_gen.astype(np.float32) / 32768.0
    
    # 只取单声道
    if len(audio_ref.shape) > 1:
        audio_ref = audio_ref[:, 0]
    if len(audio_gen.shape) > 1:
        audio_gen = audio_gen[:, 0]
    
    # 确保长度一致
    min_len = min(len(audio_ref), len(audio_gen))
    audio_ref = audio_ref[:min_len]
    audio_gen = audio_gen[:min_len]
    
    # 计算 FFT
    fft_ref = np.fft.rfft(audio_ref)
    fft_gen = np.fft.rfft(audio_gen)
    
    # 频率轴
    freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)
    
    # 计算幅度谱
    mag_ref = np.abs(fft_ref)
    mag_gen = np.abs(fft_gen)
    
    # 计算 RMS
    rms_ref = np.sqrt(np.mean(audio_ref**2))
    rms_gen = np.sqrt(np.mean(audio_gen**2))
    
    print(f"\n=== b_freq = {b_freq_value} ===")
    print(f"RMS Reference: {rms_ref:.6f}")
    print(f"RMS Generated: {rms_gen:.6f}")
    print(f"RMS Ratio (gen/ref): {rms_gen/rms_ref:.4f}")
    
    # 找到最强的谐波（忽略DC）
    # 跳过前10个bin（DC 和极低频）
    start_bin = 10
    top_bins_ref = np.argsort(mag_ref[start_bin:])[-10:] + start_bin
    top_bins_gen = np.argsort(mag_gen[start_bin:])[-10:] + start_bin
    
    print(f"\n参考音频的前10个最强谐波:")
    for i, bin_idx in enumerate(reversed(top_bins_ref)):
        freq = freqs[bin_idx]
        mag = mag_ref[bin_idx]
        print(f"  {i+1}. {freq:.2f} Hz - 幅度: {mag:.2f}")
    
    print(f"\n生成音频的前10个最强谐波:")
    for i, bin_idx in enumerate(reversed(top_bins_gen)):
        freq = freqs[bin_idx]
        mag = mag_gen[bin_idx]
        print(f"  {i+1}. {freq:.2f} Hz - 幅度: {mag:.2f}")
    
    # 分析时域特征
    # 检查包络形状
    window_size = sr_ref // 50  # 20ms窗口
    env_ref = []
    env_gen = []
    
    for i in range(0, len(audio_ref) - window_size, window_size // 2):
        env_ref.append(np.sqrt(np.mean(audio_ref[i:i+window_size]**2)))
        env_gen.append(np.sqrt(np.mean(audio_gen[i:i+window_size]**2)))
    
    env_ref = np.array(env_ref)
    env_gen = np.array(env_gen)
    
    # 找到包络峰值
    peak_ref = np.max(env_ref)
    peak_gen = np.max(env_gen)
    
    print(f"\n包络峰值:")
    print(f"  参考: {peak_ref:.6f}")
    print(f"  生成: {peak_gen:.6f}")
    print(f"  比率: {peak_gen/peak_ref:.4f}")
    
    # 计算相关度（在起音后的稳定段）
    # 跳过前10%和后10%
    start_idx = len(audio_ref) // 10
    end_idx = len(audio_ref) * 9 // 10
    
    corr = np.corrcoef(audio_ref[start_idx:end_idx], 
                       audio_gen[start_idx:end_idx])[0, 1]
    print(f"\n时域相关系数: {corr:.4f}")
    
    return {
        'b_freq': b_freq_value,
        'rms_ref': rms_ref,
        'rms_gen': rms_gen,
        'rms_ratio': rms_gen / rms_ref,
        'peak_ref': peak_ref,
        'peak_gen': peak_gen,
        'peak_ratio': peak_gen / peak_ref,
        'correlation': corr,
    }

def main():
    print("分析失败的 b_freq 测试...")
    print("=" * 80)
    
    results = []
    for b_freq in failing_tests:
        result = analyze_b_freq_value(b_freq)
        if result:
            results.append(result)
    
    # 汇总分析
    print("\n" + "=" * 80)
    print("汇总分析:")
    print("=" * 80)
    
    for r in results:
        print(f"b_freq={r['b_freq']:.4f}: "
              f"RMS比={r['rms_ratio']:.4f}, "
              f"峰值比={r['peak_ratio']:.4f}, "
              f"相关={r['correlation']:.4f}")
    
    # 绘制趋势图
    b_freqs = [r['b_freq'] for r in results]
    rms_ratios = [r['rms_ratio'] for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(b_freqs, rms_ratios, 'o-', linewidth=2, markersize=8)
    plt.axhline(y=1.0, color='r', linestyle='--', label='理想值=1.0')
    plt.xlabel('b_freq 参数值')
    plt.ylabel('RMS 比率 (生成/参考)')
    plt.title('失败测试的 RMS 比率分布')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    output_path = Path('temps/b_freq_failures_analysis.png')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"\n图表已保存到: {output_path}")

if __name__ == "__main__":
    main()
