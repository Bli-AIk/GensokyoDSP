#!/usr/bin/env python3
"""详细分析fade行为"""
import numpy as np
from scipy.io import wavfile
import sys

def analyze_file(filepath):
    sr, data = wavfile.read(filepath)
    
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 更细的时间分辨率
    chunk_size = int(sr * 0.001)  # 1ms
    times = []
    rms_values = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) == 0:
            break
        rms = np.sqrt(np.mean(chunk**2))
        rms_values.append(rms)
        times.append(i / sr)
    
    return np.array(times), np.array(rms_values)

def main():
    val = sys.argv[1] if len(sys.argv) > 1 else "1.0"
    
    ref_file = f"tests/fixtures/vol_fade_tests/vol_fade_{val}.wav"
    gen_file = f"tests/output/test_vol_fade_{val}.wav"
    
    print(f"=== vol_fade={val} ===\n")
    
    ref_times, ref_rms = analyze_file(ref_file)
    gen_times, gen_rms = analyze_file(gen_file)
    
    ref_peak = np.max(ref_rms)
    ref_peak_time = ref_times[np.argmax(ref_rms)]
    gen_peak = np.max(gen_rms)
    gen_peak_time = gen_times[np.argmax(gen_rms)]
    
    print(f"参考峰值: {ref_peak:.6f} at {ref_peak_time:.3f}s")
    print(f"生成峰值: {gen_peak:.6f} at {gen_peak_time:.3f}s")
    print(f"峰值比率: {gen_peak/ref_peak:.3f}")
    
    # 找attack time (到达峰值90%的时间)
    ref_90_idx = None
    for i, rms in enumerate(ref_rms):
        if rms >= ref_peak * 0.9:
            ref_90_idx = i
            break
    
    gen_90_idx = None
    for i, rms in enumerate(gen_rms):
        if rms >= gen_peak * 0.9:
            gen_90_idx = i
            break
    
    if ref_90_idx:
        print(f"\n参考到达90%峰值: {ref_times[ref_90_idx]:.3f}s")
    if gen_90_idx:
        print(f"生成到达90%峰值: {gen_times[gen_90_idx]:.3f}s")
    
    # 分析fade开始后的衰减
    print(f"\n衰减曲线 (从峰值开始):")
    print("时间偏移 | 参考RMS | 生成RMS | 参考% | 生成%")
    print("-" * 60)
    
    ref_peak_idx = np.argmax(ref_rms)
    gen_peak_idx = np.argmax(gen_rms)
    
    time_offsets = [0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]
    
    for offset in time_offsets:
        # 参考
        target_time = ref_peak_time + offset
        idx = np.argmin(np.abs(ref_times - target_time))
        ref_val = ref_rms[idx] if idx < len(ref_rms) else 0
        ref_pct = (ref_val / ref_peak * 100) if ref_peak > 0 else 0
        
        # 生成
        target_time = gen_peak_time + offset
        idx = np.argmin(np.abs(gen_times - target_time))
        gen_val = gen_rms[idx] if idx < len(gen_rms) else 0
        gen_pct = (gen_val / gen_peak * 100) if gen_peak > 0 else 0
        
        print(f"+{offset:.2f}s | {ref_val:.6f} | {gen_val:.6f} | {ref_pct:5.1f}% | {gen_pct:5.1f}%")

if __name__ == "__main__":
    main()
