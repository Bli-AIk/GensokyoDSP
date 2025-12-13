#!/usr/bin/env python3
"""精确分析失败测试的差异"""
import numpy as np
from scipy.io import wavfile
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

def analyze_detailed(val):
    """详细分析单个测试"""
    print(f"\n{'='*70}")
    print(f"详细分析 a_form={val}")
    print(f"{'='*70}")
    
    ref_file = f'tests/fixtures/a_form_tests/a_form_{val}.wav'
    gen_file = f'tests/output/test_a_form_{val}.wav'
    
    # 加载
    sr_ref, data_ref = wavfile.read(ref_file)
    if len(data_ref.shape) > 1:
        data_ref = data_ref[:, 0]
    data_ref = data_ref.astype(np.float64) / 2147483648.0
    
    sr_gen, data_gen = wavfile.read(gen_file)
    if len(data_gen.shape) > 1:
        data_gen = data_gen[:, 0]
    data_gen = data_gen.astype(np.float32) / 32768.0
    
    # 稳态部分
    skip = int(0.5 * sr_ref)
    ref_steady = data_ref[skip:-skip]
    gen_steady = data_gen[skip:-skip]
    
    # 基本统计
    ref_rms = np.sqrt(np.mean(ref_steady**2))
    gen_rms = np.sqrt(np.mean(gen_steady**2))
    ref_peak = np.max(np.abs(ref_steady))
    gen_peak = np.max(np.abs(gen_steady))
    
    print(f"\nRMS: 参考={ref_rms:.6f}, 生成={gen_rms:.6f}, 比例={gen_rms/ref_rms:.4f}")
    print(f"峰值: 参考={ref_peak:.6f}, 生成={gen_peak:.6f}, 比例={gen_peak/ref_peak:.4f}")
    
    # 取一个周期详细分析
    period = 92
    ref_cycle = ref_steady[:period]
    gen_cycle = gen_steady[:period]
    
    # 时域相关性
    correlation = np.corrcoef(ref_cycle, gen_cycle)[0, 1]
    print(f"单周期相关性: {correlation:.6f}")
    
    # 逐点比较
    diff = np.abs(ref_cycle - gen_cycle)
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    print(f"最大差异: {max_diff:.6f}, 平均差异: {mean_diff:.6f}")
    
    # FFT分析
    num_cycles = 10
    num_samples = period * num_cycles
    ref_fft = np.abs(np.fft.rfft(ref_steady[:num_samples] * np.hanning(num_samples)))
    gen_fft = np.abs(np.fft.rfft(gen_steady[:num_samples] * np.hanning(num_samples)))
    fft_freqs = np.fft.rfftfreq(num_samples, 1/sr_ref)
    
    freq = sr_ref / period
    
    print(f"\n谐波比较 (前10个):")
    total_error = 0
    for n in range(1, 11):
        target_freq = freq * n
        idx = np.argmin(np.abs(fft_freqs - target_freq))
        search_range = 5
        start_idx = max(0, idx - search_range)
        end_idx = min(len(ref_fft), idx + search_range + 1)
        
        ref_mag = np.max(ref_fft[start_idx:end_idx])
        gen_mag = np.max(gen_fft[start_idx:end_idx])
        
        ratio = gen_mag / ref_mag if ref_mag > 1e-6 else 0
        error = abs(1.0 - ratio)
        total_error += error
        
        if error > 0.1:  # 只显示误差大的
            print(f"  H{n}: {ref_mag:.2f} vs {gen_mag:.2f} (比例={ratio:.3f}, 误差={error:.3f}) {'!' if error > 0.2 else ''}")
    
    print(f"总谐波误差: {total_error:.3f}, 平均: {total_error/10:.3f}")
    
    # 提出改进建议
    if total_error/10 > 0.15:
        print("\n⚠️  谐波匹配度较差，需要调整傅里叶系数")
    if abs(gen_rms/ref_rms - 1.0) > 0.02:
        print(f"⚠️  RMS差异较大 ({(gen_rms/ref_rms - 1.0)*100:.1f}%)，需要调整音量校准")
    if correlation < 0.95:
        print(f"⚠️  波形相关性较低 ({correlation:.3f})，可能存在相位或形状问题")

# 分析3个失败的测试
for val in [0.7, 0.95, 1.0]:
    try:
        analyze_detailed(val)
    except Exception as e:
        print(f"\n错误 {val}: {e}")
        import traceback
        traceback.print_exc()
