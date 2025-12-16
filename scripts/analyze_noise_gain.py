#!/usr/bin/env python3
"""详细分析a_noise的噪声增益曲线"""
import numpy as np
import wave
from pathlib import Path

def read_wav(filename):
    """读取WAV文件"""
    with wave.open(filename, 'rb') as w:
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if audio.ndim > 1:
            audio = audio.reshape(-1, 2)[:, 0]
        return audio, sr

def main():
    base_dir = Path("/home/aik/Projects/RustroverProjects/gensokyo_dsp/tests/fixtures/a_noise_tests")
    
    # 收集所有a_noise值的RMS
    data = []
    for wav_file in sorted(base_dir.glob("a_noise_*.wav")):
        value = float(wav_file.stem.split('_')[-1])
        audio, sr = read_wav(str(wav_file))
        rms = np.sqrt(np.mean(audio**2))
        data.append((value, rms))
        print(f"a_noise={value:.4f}: RMS={rms:.6f}")
    
    print("\n" + "=" * 80)
    print("分析噪声增益曲线")
    print("=" * 80)
    
    # 找到基准RMS (低噪声区域的平均值)
    low_noise = [rms for val, rms in data if val < 0.75]
    base_rms = np.mean(low_noise)
    print(f"基准RMS (a_noise < 0.75): {base_rms:.6f}")
    
    # 分析高噪声区域
    print(f"\n{'a_noise':>10s} {'RMS':>12s} {'vs base':>12s} {'建议增益':>12s}")
    print("-" * 80)
    
    for val, rms in data:
        if val >= 0.75:
            ratio = rms / base_rms
            # 当前代码在a_noise=0.8时开始应用噪声
            # 我们需要找到正确的增益曲线
            gain_needed = base_rms / rms  # 需要的增益来保持RMS
            print(f"{val:>10.4f} {rms:>12.6f} {ratio:>12.4f} {gain_needed:>12.4f}")
    
    # 分析从0.8到1.0的过渡
    print("\n从当前代码推断:")
    print("- 当前代码: a_noise < 0.8 时噪声权重=0")
    print("- 当前代码: a_noise >= 0.8 时线性从0增加到0.118 (broad_weight)")
    print("- 当前代码: a_noise >= 0.8 时振荡器权重从1.0线性降到0")
    
    # 根据数据计算正确的混合曲线
    print("\n基于参考数据的正确行为:")
    
    # 找到关键点
    rms_at_0_8 = next((rms for val, rms in data if abs(val - 0.8) < 0.01), None)
    rms_at_0_85 = next((rms for val, rms in data if abs(val - 0.8502) < 0.01), None)
    rms_at_0_90 = next((rms for val, rms in data if abs(val - 0.9051) < 0.01), None)
    rms_at_0_95 = next((rms for val, rms in data if abs(val - 0.9515) < 0.01), None)
    rms_at_1_0 = next((rms for val, rms in data if abs(val - 1.0) < 0.01), None)
    
    if rms_at_0_85 and rms_at_0_90 and rms_at_0_95 and rms_at_1_0:
        print(f"  0.8502: RMS={rms_at_0_85:.6f} (下降{(1-rms_at_0_85/base_rms)*100:.1f}%)")
        print(f"  0.9051: RMS={rms_at_0_90:.6f} (下降{(1-rms_at_0_90/base_rms)*100:.1f}%)")
        print(f"  0.9515: RMS={rms_at_0_95:.6f} (下降{(1-rms_at_0_95/base_rms)*100:.1f}%)")
        print(f"  1.0000: RMS={rms_at_1_0:.6f} (下降{(1-rms_at_1_0/base_rms)*100:.1f}%)")
        
        # 推断正确的混合权重
        print("\n推荐的振荡器/噪声权重调整:")
        # 如果RMS下降，说明总能量减少，可能需要增加噪声增益或调整混合
        # 假设振荡器RMS ≈ base_rms，噪声RMS需要调整以匹配总RMS
        
        # 对于0.8502
        t_85 = (0.8502 - 0.8) / 0.2  # = 0.251
        expected_rms_85_current = base_rms  # 假设当前实现
        actual_ratio_85 = rms_at_0_85 / base_rms
        print(f"  0.8502 (t={t_85:.3f}): 实际RMS比例={actual_ratio_85:.4f}")
        
        t_90 = (0.9051 - 0.8) / 0.2
        actual_ratio_90 = rms_at_0_90 / base_rms
        print(f"  0.9051 (t={t_90:.3f}): 实际RMS比例={actual_ratio_90:.4f}")
        
        t_95 = (0.9515 - 0.8) / 0.2
        actual_ratio_95 = rms_at_0_95 / base_rms
        print(f"  0.9515 (t={t_95:.3f}): 实际RMS比例={actual_ratio_95:.4f}")

if __name__ == "__main__":
    main()
