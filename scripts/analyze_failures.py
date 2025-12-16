#!/usr/bin/env python3
"""分析失败的测试用例"""
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

def analyze_audio(audio, sr, name=""):
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
    
    print(f"{name:20s} - RMS: {rms:.6f}, Peak: {peak:.6f}, Peak Freq: {peak_freq:.2f} Hz")
    
    return {
        'rms': rms,
        'peak': peak,
        'peak_freq': peak_freq,
        'magnitude': magnitude,
        'freqs': freqs
    }

def compare_wavs(ref_file, gen_file):
    """比较两个WAV文件"""
    if not os.path.exists(ref_file):
        print(f"参考文件不存在: {ref_file}")
        return None
    if not os.path.exists(gen_file):
        print(f"生成文件不存在: {gen_file}")
        return None
    
    ref_audio, ref_sr = read_wav(ref_file)
    gen_audio, gen_sr = read_wav(gen_file)
    
    print(f"\n比较: {os.path.basename(ref_file)}")
    ref_stats = analyze_audio(ref_audio, ref_sr, "参考")
    gen_stats = analyze_audio(gen_audio, gen_sr, "生成")
    
    # 计算差异
    rms_diff = abs(ref_stats['rms'] - gen_stats['rms'])
    rms_ratio = gen_stats['rms'] / ref_stats['rms'] if ref_stats['rms'] > 0 else 0
    
    print(f"RMS差异: {rms_diff:.6f} (比例: {rms_ratio:.4f})")
    print(f"峰值差异: {abs(ref_stats['peak'] - gen_stats['peak']):.6f}")
    
    return {
        'ref': ref_stats,
        'gen': gen_stats,
        'rms_diff': rms_diff,
        'rms_ratio': rms_ratio
    }

def main():
    base_dir = Path("/home/aik/Projects/RustroverProjects/gensokyo_dsp")
    
    # 失败的测试
    failures = {
        'a_noise': [0.8502, 0.9051, 0.9515, 1.0],
        'b_freq': [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051],
        'osc_mix': [0.8502]
    }
    
    print("=" * 80)
    print("分析失败的测试用例")
    print("=" * 80)
    
    for test_type, values in failures.items():
        print(f"\n\n{'=' * 80}")
        print(f"测试类型: {test_type}")
        print(f"{'=' * 80}")
        
        for value in values:
            ref_file = base_dir / f"tests/fixtures/{test_type}_tests/{test_type}_{value}.wav"
            gen_file = base_dir / f"temps/generated_{test_type}_{value}.wav"
            
            result = compare_wavs(str(ref_file), str(gen_file))
            
            if result and test_type == 'a_noise':
                # 对于a_noise，分析噪声增益
                rms_ratio = result['rms_ratio']
                print(f"建议的噪声增益调整: {1.0/rms_ratio:.4f}")
            
            if result and test_type == 'b_freq':
                # 对于b_freq，分析频率比例
                ref_freq = result['ref']['peak_freq']
                gen_freq = result['gen']['peak_freq']
                print(f"频率匹配: 参考={ref_freq:.2f} Hz, 生成={gen_freq:.2f} Hz")

if __name__ == "__main__":
    main()
