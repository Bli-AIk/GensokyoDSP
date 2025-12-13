#!/usr/bin/env python3
"""检查波形的相位特征"""
import numpy as np
from scipy.io import wavfile
import warnings
warnings.filterwarnings('ignore')

def check_waveform_shape(val):
    """检查波形形状"""
    print(f"\n{'='*60}")
    print(f"a_form={val}")
    print(f"{'='*60}")
    
    ref_file = f'tests/fixtures/a_form_tests/a_form_{val}.wav'
    gen_file = f'tests/output/test_a_form_{val}.wav'
    
    # 参考
    sr, data = wavfile.read(ref_file)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float64) / 2147483648.0
    skip = int(0.5 * sr)
    ref_cycle = data[skip:skip+92]
    
    # 生成
    sr, data = wavfile.read(gen_file)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    gen_cycle = data[skip:skip+92]
    
    # 显示前20个采样点
    print("参考前20点:", ref_cycle[:20])
    print("生成前20点:", gen_cycle[:20])
    
    # 检查上升/下降趋势
    ref_starts_positive = ref_cycle[0] > 0
    gen_starts_positive = gen_cycle[0] > 0
    
    print(f"\n参考起始: {'正' if ref_starts_positive else '负'}")
    print(f"生成起始: {'正' if gen_starts_positive else '负'}")
    
    # 尝试反相生成的波形
    gen_inverted = -gen_cycle
    corr_normal = np.corrcoef(ref_cycle, gen_cycle)[0, 1]
    corr_inverted = np.corrcoef(ref_cycle, gen_inverted)[0, 1]
    
    print(f"\n相关性(正常): {corr_normal:.4f}")
    print(f"相关性(反相): {corr_inverted:.4f}")
    
    if abs(corr_inverted) > abs(corr_normal):
        print("⚠️  生成的波形应该反相！")

# 检查0.7
check_waveform_shape(0.7)
