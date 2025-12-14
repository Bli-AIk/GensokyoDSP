#!/usr/bin/env python3
"""检查边界测试用例"""
import numpy as np
from scipy.io import wavfile

def check_case(val):
    ref_file = f"tests/fixtures/a_noise_tests/a_noise_{val}.wav"
    gen_file = f"tests/output/test_a_noise_{val}.wav"
    
    sr1, data1 = wavfile.read(ref_file)
    sr2, data2 = wavfile.read(gen_file)
    
    if data1.dtype == np.int16:
        data1 = data1.astype(np.float64) / 32768.0
        data2 = data2.astype(np.float64) / 32768.0
    
    if len(data1.shape) > 1:
        data1 = data1[:, 0]
        data2 = data2[:, 0]
    
    # RMS
    rms1 = np.sqrt(np.mean(data1**2))
    rms2 = np.sqrt(np.mean(data2**2))
    
    # 零交叉率
    zc1 = np.sum(np.abs(np.diff(np.sign(data1)))) / (2 * len(data1))
    zc2 = np.sum(np.abs(np.diff(np.sign(data2)))) / (2 * len(data2))
    
    # 简单频谱峰值
    mid = len(data1) // 2
    seg1 = data1[mid:mid+sr1]
    seg2 = data2[mid:mid+sr2]
    
    fft1 = np.abs(np.fft.rfft(seg1))
    fft2 = np.abs(np.fft.rfft(seg2))
    freqs = np.fft.rfftfreq(len(seg1), 1/sr1)
    
    # 基频能量
    fund_idx = np.argmin(np.abs(freqs - 523.25))
    fund1 = fft1[fund_idx]
    fund2 = fft2[fund_idx]
    
    print(f"\na_noise = {val}:")
    print(f"  RMS:       {rms1:.6f} vs {rms2:.6f}  (ratio: {rms2/rms1*100:.2f}%)")
    print(f"  ZCR:       {zc1:.6f} vs {zc2:.6f}  (ratio: {zc2/zc1*100:.2f}%)")
    print(f"  Fund:      {fund1:.2f} vs {fund2:.2f}  (ratio: {fund2/fund1*100:.2f}%)")
    
# 检查失败的边界值
vals = ["0.0547", "0.1058", "0.1496", "0.2007", "0.8080", "0.8502", "0.9051", "0.9515", "1.0"]
for val in vals:
    try:
        check_case(val)
    except Exception as e:
        print(f"Error for {val}: {e}")
