#!/usr/bin/env python3
"""
深入分析osc_mix_0.8502失败原因
"""

import numpy as np
import wave
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(str(filename), 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        frames = wav.readframes(n_frames)
        
        if sample_width == 2:
            data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:
            data = np.frombuffer(frames, dtype=np.int32)
        else:
            raise ValueError(f"不支持的采样位深: {sample_width}")
        
        data = data.astype(np.float64) / (2**(sample_width * 8 - 1))
        
        if n_channels == 2:
            data = data[::2]
        
        return data, framerate

def main():
    base_path = Path("/workspaces/GensokyoDSP")
    
    ref_file = base_path / "tests" / "fixtures" / "osc_mix_tests" / "osc_mix_0.8502.wav"
    test_file = base_path / "tests" / "output" / "test_osc_mix_0.8502.wav"
    
    ref_data, ref_sr = read_wav(ref_file)
    test_data, test_sr = read_wav(test_file)
    
    print("osc_mix=0.8502 详细分析:")
    print("=" * 80)
    
    # 整体RMS
    ref_rms = np.sqrt(np.mean(ref_data**2))
    test_rms = np.sqrt(np.mean(test_data**2))
    
    print(f"参考 RMS: {ref_rms:.6f}")
    print(f"测试 RMS: {test_rms:.6f}")
    print(f"RMS比例: {test_rms/ref_rms:.6f}")
    print(f"需要增益调整: {ref_rms/test_rms:.6f}")
    
    # 峰值
    ref_peak = np.max(np.abs(ref_data))
    test_peak = np.max(np.abs(test_data))
    
    print(f"\n参考峰值: {ref_peak:.6f}")
    print(f"测试峰值: {test_peak:.6f}")
    print(f"峰值比例: {test_peak/ref_peak:.6f}")
    
    # 稳态RMS（后半段）
    half = len(ref_data) // 2
    ref_steady = np.sqrt(np.mean(ref_data[half:]**2))
    test_steady = np.sqrt(np.mean(test_data[half:]**2))
    
    print(f"\n参考稳态RMS: {ref_steady:.6f}")
    print(f"测试稳态RMS: {test_steady:.6f}")
    print(f"稳态比例: {test_steady/ref_steady:.6f}")
    
    # 时间段分析
    print("\n时间段RMS分析 (100ms):")
    print(f"{'时间(s)':<10} {'参考':<12} {'测试':<12} {'差异':<12}")
    print("-" * 50)
    
    segment_dur = 0.1
    segment_samples = int(segment_dur * ref_sr)
    
    for i in range(10):
        start = i * segment_samples
        end = start + segment_samples
        
        if end > len(ref_data):
            break
        
        seg_ref = np.sqrt(np.mean(ref_data[start:end]**2))
        seg_test = np.sqrt(np.mean(test_data[start:end]**2))
        diff = abs(seg_ref - seg_test)
        
        print(f"{i*segment_dur:<10.2f} {seg_ref:<12.6f} {seg_test:<12.6f} {diff:<12.6f}")
    
    # 相关系数
    min_len = min(len(ref_data), len(test_data))
    correlation = np.corrcoef(ref_data[:min_len], test_data[:min_len])[0, 1]
    print(f"\n相关系数: {correlation:.6f}")
    
    # 频谱分析（前512样本）
    fft_size = 512
    ref_fft = np.abs(np.fft.rfft(ref_data[:fft_size]))
    test_fft = np.abs(np.fft.rfft(test_data[:fft_size]))
    
    freqs = np.fft.rfftfreq(fft_size, 1/ref_sr)
    
    print("\n主要频率成分 (前5个):")
    print("参考:")
    top_ref = np.argsort(ref_fft)[-5:][::-1]
    for idx in top_ref:
        print(f"  {freqs[idx]:.1f} Hz: {ref_fft[idx]:.3f}")
    
    print("测试:")
    top_test = np.argsort(test_fft)[-5:][::-1]
    for idx in top_test:
        print(f"  {freqs[idx]:.1f} Hz: {test_fft[idx]:.3f}")

if __name__ == "__main__":
    main()
