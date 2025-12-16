#!/usr/bin/env python3
"""
分析b_freq测试的频率关系
"""
import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path

# b_freq测试用例
B_FREQ_TESTS = {
    0.4958: "b_freq_0.4958.wav",
    0.5506: "b_freq_0.5506.wav",
    0.6519: "b_freq_0.6519.wav",
    0.8080: "b_freq_0.8080.wav",
    0.8502: "b_freq_0.8502.wav",
    0.9051: "b_freq_0.9051.wav",
}

def detect_fundamental(audio_file, sr):
    """检测音频的基频"""
    # 使用FFT检测主要频率
    fft = np.fft.rfft(audio_file)
    freqs = np.fft.rfftfreq(len(audio_file), 1/sr)
    magnitude = np.abs(fft)
    
    # 找到最强的频率成分
    peak_idx = np.argmax(magnitude)
    fundamental = freqs[peak_idx]
    
    # 找到前几个峰值
    peaks, _ = signal.find_peaks(magnitude, height=np.max(magnitude)*0.1)
    peak_freqs = freqs[peaks]
    peak_mags = magnitude[peaks]
    
    # 按幅度排序
    sorted_indices = np.argsort(peak_mags)[::-1]
    top_freqs = peak_freqs[sorted_indices[:10]]
    top_mags = peak_mags[sorted_indices[:10]]
    
    return fundamental, top_freqs, top_mags

def main():
    fixtures_dir = Path('/workspaces/GensokyoDSP/tests/fixtures/b_freq_tests')
    
    # a_freq=0.5 对应 523Hz
    base_freq = 523.2511
    
    print("=" * 80)
    print("b_freq频率分析")
    print(f"基准频率 (a_freq=0.5): {base_freq:.2f} Hz")
    print("=" * 80)
    
    for b_freq_param, filename in B_FREQ_TESTS.items():
        filepath = fixtures_dir / filename
        
        if not filepath.exists():
            print(f"\n✗ {b_freq_param:.4f}: 文件不存在")
            continue
        
        data, sr = sf.read(filepath)
        if len(data.shape) > 1:
            data = data[:, 0]
        
        fundamental, top_freqs, top_mags = detect_fundamental(data, sr)
        
        print(f"\nb_freq = {b_freq_param:.4f}")
        print(f"  主要频率: {fundamental:.2f} Hz")
        print(f"  频率比: {fundamental/base_freq:.6f}")
        print(f"  前5个峰值频率:")
        for i in range(min(5, len(top_freqs))):
            print(f"    {top_freqs[i]:.2f} Hz (幅度: {top_mags[i]:.2f})")

if __name__ == '__main__':
    main()
