#!/usr/bin/env python3
"""分析失败的测试用例，寻找频率和相位问题"""

import numpy as np
import wave
import struct
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # 非GUI后端
import matplotlib.pyplot as plt

def load_wav(filepath):
    """加载WAV文件"""
    with wave.open(str(filepath), 'r') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        frames = wav_file.readframes(n_frames)
        
        if sample_width == 2:  # 16-bit
            samples = struct.unpack(f'{n_frames * n_channels}h', frames)
        else:
            raise ValueError(f"不支持的采样宽度: {sample_width}")
        
        # 转换为numpy数组并归一化
        audio = np.array(samples, dtype=np.float32) / 32768.0
        
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
            # 混合为单声道
            audio = np.mean(audio, axis=1)
        
        return audio, framerate

def analyze_frequency_content(audio, sample_rate, name):
    """分析频率内容"""
    # 只分析前面一部分（避免衰减影响）
    window_size = min(len(audio), sample_rate * 2)  # 2秒窗口
    windowed = audio[:window_size]
    
    # 应用汉明窗
    windowed = windowed * np.hamming(len(windowed))
    
    # FFT
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1/sample_rate)
    magnitudes = np.abs(fft)
    
    # 找到主要频率峰值
    peaks_idx = []
    threshold = np.max(magnitudes) * 0.1  # 10%阈值
    
    for i in range(1, len(magnitudes) - 1):
        if magnitudes[i] > threshold and magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1]:
            peaks_idx.append(i)
    
    # 排序峰值（按幅度）
    peaks_idx = sorted(peaks_idx, key=lambda i: magnitudes[i], reverse=True)[:10]
    
    print(f"\n{name} 频率分析:")
    print("  主要频率峰值:")
    for i, idx in enumerate(peaks_idx[:5]):
        print(f"    {i+1}. {freqs[idx]:.2f} Hz (幅度: {magnitudes[idx]:.1f})")
    
    return freqs, magnitudes, peaks_idx

def compare_audio_detail(ref_audio, test_audio, sample_rate, test_name):
    """详细比较两个音频"""
    print(f"\n{'='*60}")
    print(f"详细分析: {test_name}")
    print(f"{'='*60}")
    
    # 确保长度相同
    min_len = min(len(ref_audio), len(test_audio))
    ref = ref_audio[:min_len]
    test = test_audio[:min_len]
    
    # 基本统计
    print(f"\n基本统计:")
    print(f"  参考音频 RMS: {np.sqrt(np.mean(ref**2)):.6f}")
    print(f"  测试音频 RMS: {np.sqrt(np.mean(test**2)):.6f}")
    print(f"  参考音频峰值: {np.max(np.abs(ref)):.6f}")
    print(f"  测试音频峰值: {np.max(np.abs(test)):.6f}")
    
    # 频率分析
    ref_freqs, ref_mags, ref_peaks = analyze_frequency_content(ref, sample_rate, "参考音频")
    test_freqs, test_mags, test_peaks = analyze_frequency_content(test, sample_rate, "测试音频")
    
    # 相位和时域分析
    print(f"\n时域分析:")
    diff = ref - test
    print(f"  平均差异: {np.mean(diff):.6f}")
    print(f"  差异RMS: {np.sqrt(np.mean(diff**2)):.6f}")
    print(f"  最大差异: {np.max(np.abs(diff)):.6f}")
    
    # 相关性分析
    correlation = np.corrcoef(ref, test)[0, 1]
    print(f"  相关系数: {correlation:.6f}")
    
    # 查找最大差异位置
    max_diff_idx = np.argmax(np.abs(diff))
    max_diff_time = max_diff_idx / sample_rate
    print(f"  最大差异位置: {max_diff_time:.3f}秒 (样本 {max_diff_idx})")
    
    # 生成对比图
    generate_comparison_plot(ref, test, sample_rate, test_name, ref_mags, test_mags, ref_freqs)

def generate_comparison_plot(ref, test, sr, name, ref_mags, test_mags, freqs):
    """生成对比图"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 时域对比（前0.1秒）
    duration = 0.1
    samples = int(sr * duration)
    time = np.arange(samples) / sr
    
    axes[0].plot(time, ref[:samples], label='参考', alpha=0.7)
    axes[0].plot(time, test[:samples], label='测试', alpha=0.7)
    axes[0].set_xlabel('时间 (秒)')
    axes[0].set_ylabel('幅度')
    axes[0].set_title(f'{name} - 时域对比（前{duration}秒）')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 差异波形
    axes[1].plot(time, (ref - test)[:samples])
    axes[1].set_xlabel('时间 (秒)')
    axes[1].set_ylabel('差异')
    axes[1].set_title('差异波形')
    axes[1].grid(True, alpha=0.3)
    
    # 频谱对比
    axes[2].plot(freqs[:len(freqs)//10], ref_mags[:len(ref_mags)//10], label='参考', alpha=0.7)
    axes[2].plot(freqs[:len(freqs)//10], test_mags[:len(test_mags)//10], label='测试', alpha=0.7)
    axes[2].set_xlabel('频率 (Hz)')
    axes[2].set_ylabel('幅度')
    axes[2].set_title('频谱对比（低频部分）')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim(0, 5000)  # 只显示0-5kHz
    
    plt.tight_layout()
    
    # 保存图像
    output_dir = Path('temps/analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = name.replace('/', '_').replace(' ', '_')
    plt.savefig(output_dir / f'{safe_name}_analysis.png', dpi=150)
    plt.close()
    print(f"\n  已保存分析图: temps/analysis/{safe_name}_analysis.png")

def main():
    """主函数"""
    # 失败的测试用例
    failed_tests = [
        ('b_freq', 0.4958),
        ('b_freq', 0.5506),
        ('b_freq', 0.6519),
        ('b_freq', 0.8080),
        ('b_freq', 0.8502),
        ('b_freq', 0.9051),
    ]
    
    print("分析失败的b_freq测试用例")
    print("="*60)
    
    for param_name, value in failed_tests:
        # 构造文件路径
        test_name = f"{param_name}_{value}"
        ref_path = Path(f"tests/fixtures/{param_name}_tests/{param_name}_{value}.wav")
        test_path = Path(f"tests/output/test_{param_name}_{value}.wav")
        
        if not ref_path.exists():
            print(f"\n警告: 参考文件不存在: {ref_path}")
            continue
        
        if not test_path.exists():
            print(f"\n警告: 测试文件不存在: {test_path}")
            continue
        
        # 加载音频
        ref_audio, ref_sr = load_wav(ref_path)
        test_audio, test_sr = load_wav(test_path)
        
        if ref_sr != test_sr:
            print(f"\n警告: 采样率不匹配: {ref_sr} vs {test_sr}")
            continue
        
        # 详细分析
        compare_audio_detail(ref_audio, test_audio, ref_sr, test_name)
    
    print("\n" + "="*60)
    print("分析完成！")

if __name__ == '__main__':
    main()
