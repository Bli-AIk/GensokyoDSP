#!/usr/bin/env python3
"""
对比测试输出与参考文件的频率
"""
import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path

# 失败的b_freq测试
B_FREQ_TESTS = [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051]

def detect_fundamental(audio_file, sr):
    """检测音频的基频"""
    fft = np.fft.rfft(audio_file)
    freqs = np.fft.rfftfreq(len(audio_file), 1/sr)
    magnitude = np.abs(fft)
    
    # 找到最强的频率成分
    peak_idx = np.argmax(magnitude)
    fundamental = freqs[peak_idx]
    
    return fundamental

def main():
    fixtures_dir = Path('/workspaces/GensokyoDSP/tests/fixtures/b_freq_tests')
    output_dir = Path('/workspaces/GensokyoDSP/tests/output')
    
    base_freq = 523.2511
    
    print("=" * 80)
    print("b_freq测试输出与参考对比")
    print("=" * 80)
    
    for b_freq_param in B_FREQ_TESTS:
        value_str = f"{b_freq_param:.4f}"
        ref_file = fixtures_dir / f"b_freq_{value_str}.wav"
        test_file = output_dir / f"test_b_freq_{value_str}.wav"
        
        if not ref_file.exists() or not test_file.exists():
            print(f"\n✗ {value_str}: 文件缺失")
            continue
        
        ref_data, ref_sr = sf.read(ref_file)
        test_data, test_sr = sf.read(test_file)
        
        if len(ref_data.shape) > 1:
            ref_data = ref_data[:, 0]
        if len(test_data.shape) > 1:
            test_data = test_data[:, 0]
        
        ref_freq = detect_fundamental(ref_data, ref_sr)
        test_freq = detect_fundamental(test_data, test_sr)
        
        ref_ratio = ref_freq / base_freq
        test_ratio = test_freq / base_freq
        
        ref_rms = np.sqrt(np.mean(ref_data**2))
        test_rms = np.sqrt(np.mean(test_data**2))
        
        print(f"\nb_freq = {value_str}")
        print(f"  参考:")
        print(f"    频率: {ref_freq:.2f} Hz (比例: {ref_ratio:.6f})")
        print(f"    RMS: {ref_rms:.6f}")
        print(f"  测试:")
        print(f"    频率: {test_freq:.2f} Hz (比例: {test_ratio:.6f})")
        print(f"    RMS: {test_rms:.6f}")
        print(f"  差异:")
        print(f"    频率差: {abs(ref_freq - test_freq):.2f} Hz ({abs(ref_ratio - test_ratio)/ref_ratio*100:.2f}%)")
        print(f"    RMS差: {abs(ref_rms - test_rms):.6f} ({abs(ref_rms - test_rms)/ref_rms*100:.2f}%)")

if __name__ == '__main__':
    main()
