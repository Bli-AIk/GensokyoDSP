#!/usr/bin/env python3
"""
详细分析b_freq失败测试的波形特征
"""
import numpy as np
import soundfile as sf
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B_FREQ_TESTS = [0.4958, 0.5506, 0.6519, 0.8080, 0.8502, 0.9051]

def analyze_waveform_detail(data, sr, freq):
    """详细分析波形"""
    # 计算周期数
    period = sr / freq
    n_periods = int(len(data) / period)
    
    # 提取中间几个周期
    start_period = n_periods // 2
    start_idx = int(start_period * period)
    end_idx = int((start_period + 10) * period)
    
    if end_idx > len(data):
        end_idx = len(data)
    
    segment = data[start_idx:end_idx]
    
    # 计算统计信息
    rms = np.sqrt(np.mean(segment**2))
    peak = np.max(np.abs(segment))
    crest_factor = peak / rms if rms > 0 else 0
    
    # 计算频谱
    fft = np.fft.rfft(segment)
    freqs = np.fft.rfftfreq(len(segment), 1/sr)
    magnitude = np.abs(fft)
    
    # 找到谐波
    harmonics = []
    for n in range(1, 11):
        harmonic_freq = freq * n
        # 找到最接近的频率bin
        idx = np.argmin(np.abs(freqs - harmonic_freq))
        harmonics.append((n, freqs[idx], magnitude[idx]))
    
    return {
        'rms': rms,
        'peak': peak,
        'crest_factor': crest_factor,
        'harmonics': harmonics,
        'segment': segment,
    }

def main():
    fixtures_dir = Path('/workspaces/GensokyoDSP/tests/fixtures/b_freq_tests')
    output_dir = Path('/workspaces/GensokyoDSP/tests/output')
    plot_dir = Path('/workspaces/GensokyoDSP/scripts/analysis/plots')
    plot_dir.mkdir(exist_ok=True)
    
    base_freq = 523.2511
    
    print("=" * 80)
    print("b_freq波形详细分析")
    print("=" * 80)
    
    for b_freq_param in B_FREQ_TESTS:
        value_str = f"{b_freq_param:.4f}"
        ref_file = fixtures_dir / f"b_freq_{value_str}.wav"
        test_file = output_dir / f"test_b_freq_{value_str}.wav"
        
        if not ref_file.exists() or not test_file.exists():
            continue
        
        ref_data, ref_sr = sf.read(ref_file)
        test_data, test_sr = sf.read(test_file)
        
        if len(ref_data.shape) > 1:
            ref_data = ref_data[:, 0]
        if len(test_data.shape) > 1:
            test_data = test_data[:, 0]
        
        # 根据之前的分析，获取实际频率
        freq_ratios = {
            0.4958: 0.124969,
            0.5506: 0.249394,
            0.6519: 0.588907,
            0.8080: 3.999829,
            0.8502: 7.174971,
            0.9051: 10.644159,
        }
        
        actual_freq = base_freq * freq_ratios[b_freq_param]
        
        ref_analysis = analyze_waveform_detail(ref_data, ref_sr, actual_freq)
        test_analysis = analyze_waveform_detail(test_data, test_sr, actual_freq)
        
        print(f"\nb_freq = {value_str} ({actual_freq:.2f} Hz)")
        print(f"  参考波形:")
        print(f"    RMS: {ref_analysis['rms']:.6f}")
        print(f"    峰值: {ref_analysis['peak']:.6f}")
        print(f"    峰值因数: {ref_analysis['crest_factor']:.3f}")
        print(f"  测试波形:")
        print(f"    RMS: {test_analysis['rms']:.6f}")
        print(f"    峰值: {test_analysis['peak']:.6f}")
        print(f"    峰值因数: {test_analysis['crest_factor']:.3f}")
        
        print(f"  谐波对比 (前5个):")
        for i in range(min(5, len(ref_analysis['harmonics']))):
            n_ref, freq_ref, mag_ref = ref_analysis['harmonics'][i]
            n_test, freq_test, mag_test = test_analysis['harmonics'][i]
            ratio = mag_test / mag_ref if mag_ref > 0 else 0
            print(f"    H{n_ref}: 参考 {mag_ref:.2f}, 测试 {mag_test:.2f} (比例: {ratio:.3f})")
        
        # 绘制波形对比
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 时域
        time_ref = np.arange(len(ref_analysis['segment'])) / ref_sr
        time_test = np.arange(len(test_analysis['segment'])) / test_sr
        ax1.plot(time_ref[:1000], ref_analysis['segment'][:1000], label='参考', alpha=0.7)
        ax1.plot(time_test[:1000], test_analysis['segment'][:1000], label='测试', alpha=0.7)
        ax1.set_xlabel('时间 (s)')
        ax1.set_ylabel('幅度')
        ax1.set_title(f'b_freq={value_str} 波形对比')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 频域
        ref_fft = np.fft.rfft(ref_analysis['segment'])
        test_fft = np.fft.rfft(test_analysis['segment'])
        ref_freqs = np.fft.rfftfreq(len(ref_analysis['segment']), 1/ref_sr)
        test_freqs = np.fft.rfftfreq(len(test_analysis['segment']), 1/test_sr)
        
        ax2.plot(ref_freqs, 20*np.log10(np.abs(ref_fft)+1e-10), label='参考', alpha=0.7)
        ax2.plot(test_freqs, 20*np.log10(np.abs(test_fft)+1e-10), label='测试', alpha=0.7)
        ax2.set_xlabel('频率 (Hz)')
        ax2.set_ylabel('幅度 (dB)')
        ax2.set_title('频谱对比')
        ax2.set_xlim([0, 20000])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(plot_dir / f'b_freq_{value_str}.png', dpi=100)
        plt.close()
        
        print(f"  图表已保存: plots/b_freq_{value_str}.png")

if __name__ == '__main__':
    main()
