#!/usr/bin/env python3
"""直接分析参考音频文件"""
import numpy as np
import wave
import os
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(filename, 'rb') as w:
        sr = w.getframerate()
        n_channels = w.getnchannels()
        frames = w.readframes(w.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if n_channels == 2:
            audio = audio.reshape(-1, 2)
        return audio, sr

def analyze_audio(audio, sr):
    """分析音频特征"""
    if len(audio.shape) > 1:
        # 取单声道
        audio = audio[:, 0]
    
    rms = np.sqrt(np.mean(audio**2))
    peak = np.max(np.abs(audio))
    
    # 频谱分析
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    magnitude = np.abs(fft)
    
    # 找到峰值频率
    peak_idx = np.argmax(magnitude)
    peak_freq = freqs[peak_idx]
    
    # 找到基频区域的能量 (500-550 Hz)
    fund_mask = (freqs >= 500) & (freqs <= 550)
    fund_energy = np.sum(magnitude[fund_mask]**2)
    
    # 高频能量 (2000+ Hz)
    hf_mask = freqs >= 2000
    hf_energy = np.sum(magnitude[hf_mask]**2)
    
    total_energy = np.sum(magnitude**2)
    
    return {
        'rms': rms,
        'peak': peak,
        'peak_freq': peak_freq,
        'fund_energy': fund_energy,
        'hf_energy': hf_energy,
        'total_energy': total_energy,
        'hf_ratio': hf_energy / total_energy if total_energy > 0 else 0
    }

def main():
    base_dir = Path("/home/aik/Projects/RustroverProjects/gensokyo_dsp/tests/fixtures")
    
    # 分析a_noise测试
    print("=" * 80)
    print("分析 a_noise 参数")
    print("=" * 80)
    print(f"{'a_noise':>10s} {'RMS':>12s} {'Peak':>12s} {'Peak Freq':>12s} {'HF Ratio':>12s}")
    print("-" * 80)
    
    a_noise_values = [0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 
                      0.354, 0.4051, 0.4536, 0.4958, 0.5506, 0.6055, 
                      0.6519, 0.7025, 0.7489, 0.808, 0.8502, 0.9051, 
                      0.9515, 1.0]
    
    a_noise_stats = []
    for value in a_noise_values:
        wav_file = base_dir / "a_noise_tests" / f"a_noise_{value}.wav"
        if wav_file.exists():
            audio, sr = read_wav(str(wav_file))
            stats = analyze_audio(audio, sr)
            a_noise_stats.append((value, stats))
            print(f"{value:>10.4f} {stats['rms']:>12.6f} {stats['peak']:>12.6f} "
                  f"{stats['peak_freq']:>12.2f} {stats['hf_ratio']:>12.6f}")
    
    # 找到转折点
    print("\n分析噪声增益的转折点:")
    for i in range(1, len(a_noise_stats)):
        prev_val, prev_stats = a_noise_stats[i-1]
        curr_val, curr_stats = a_noise_stats[i]
        rms_change = (curr_stats['rms'] - prev_stats['rms']) / prev_stats['rms']
        if abs(rms_change) > 0.05:  # 5%以上变化
            print(f"  {prev_val:.4f} -> {curr_val:.4f}: RMS变化 {rms_change*100:.2f}%")
    
    # 分析b_freq测试
    print("\n" + "=" * 80)
    print("分析 b_freq 参数")
    print("=" * 80)
    print(f"{'b_freq':>10s} {'RMS':>12s} {'Peak':>12s} {'Peak Freq':>12s}")
    print("-" * 80)
    
    b_freq_values = [0.4536, 0.4958, 0.5506, 0.6055, 0.6519, 0.7025, 
                     0.7489, 0.8080, 0.8502, 0.9051, 0.9515]
    
    for value in b_freq_values:
        wav_file = base_dir / "b_freq_tests" / f"b_freq_{value}.wav"
        if wav_file.exists():
            audio, sr = read_wav(str(wav_file))
            stats = analyze_audio(audio, sr)
            print(f"{value:>10.4f} {stats['rms']:>12.6f} {stats['peak']:>12.6f} "
                  f"{stats['peak_freq']:>12.2f}")
        else:
            print(f"{value:>10.4f} 文件不存在")
    
    # 分析osc_mix测试
    print("\n" + "=" * 80)
    print("分析 osc_mix 参数")
    print("=" * 80)
    print(f"{'osc_mix':>10s} {'RMS':>12s} {'Peak':>12s}")
    print("-" * 80)
    
    osc_mix_values = [0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 
                      0.354, 0.4051, 0.4536, 0.4958, 0.5506, 0.6055, 
                      0.6519, 0.7025, 0.7489, 0.808, 0.8502, 0.9051, 
                      0.9515, 1.0]
    
    osc_mix_stats = []
    for value in osc_mix_values:
        wav_file = base_dir / "osc_mix_tests" / f"osc_mix_{value}.wav"
        if wav_file.exists():
            audio, sr = read_wav(str(wav_file))
            stats = analyze_audio(audio, sr)
            osc_mix_stats.append((value, stats))
            print(f"{value:>10.4f} {stats['rms']:>12.6f} {stats['peak']:>12.6f}")
    
    # 分析RMS趋势
    print("\n分析 osc_mix 的 RMS 趋势:")
    for i in range(1, len(osc_mix_stats)):
        prev_val, prev_stats = osc_mix_stats[i-1]
        curr_val, curr_stats = osc_mix_stats[i]
        rms_change = (curr_stats['rms'] - prev_stats['rms']) / prev_stats['rms']
        if abs(rms_change) > 0.01:  # 1%以上变化
            print(f"  {prev_val:.4f} -> {curr_val:.4f}: RMS变化 {rms_change*100:.2f}%")

if __name__ == "__main__":
    main()
