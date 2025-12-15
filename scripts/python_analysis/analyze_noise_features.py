#!/usr/bin/env python3
"""
分析噪声测试的音频特征
"""
import wave
import struct
import math
from pathlib import Path

def analyze_wav(filepath):
    """分析WAV文件的统计特征"""
    with wave.open(str(filepath), 'rb') as w:
        frames = w.readframes(w.getnframes())
        # 解析16位PCM数据
        samples = struct.unpack(f'{len(frames)//2}h', frames)
        data = [s / 32768.0 for s in samples]
        
        # 只分析第一声道
        if w.getnchannels() == 2:
            data = data[::2]
        
        # 取中间部分分析
        start = len(data) // 4
        end = len(data) * 3 // 4
        data = data[start:end]
        
        # RMS
        rms = math.sqrt(sum(x*x for x in data) / len(data))
        
        # Peak
        peak = max(abs(x) for x in data)
        
        # Crest factor
        crest = peak / (rms + 1e-10)
        
        # 零交叉率
        zero_crossings = sum(1 for i in range(len(data)-1) 
                            if (data[i] >= 0) != (data[i+1] >= 0))
        zcr = zero_crossings / len(data)
        
        # 标准差
        mean = sum(data) / len(data)
        variance = sum((x - mean)**2 for x in data) / len(data)
        std = math.sqrt(variance)
        
        return {
            'rms': rms,
            'peak': peak,
            'crest': crest,
            'zcr': zcr,
            'std': std
        }

def compare_features(ref_features, out_features):
    """比较两组特征"""
    rms_ratio = min(ref_features['rms'], out_features['rms']) / max(ref_features['rms'], out_features['rms'], 1e-10)
    std_ratio = min(ref_features['std'], out_features['std']) / max(ref_features['std'], out_features['std'], 1e-10)
    zcr_ratio = min(ref_features['zcr'], out_features['zcr']) / max(ref_features['zcr'], out_features['zcr'], 1e-10)
    peak_ratio = min(ref_features['peak'], out_features['peak']) / max(ref_features['peak'], out_features['peak'], 1e-10)
    
    crest_diff = abs(ref_features['crest'] - out_features['crest'])
    crest_sim = math.exp(-crest_diff / 2.0)
    
    similarity = (rms_ratio * 0.80 + std_ratio * 0.18 + zcr_ratio * 0.01 + 
                  crest_sim * 0.007 + peak_ratio * 0.003) * 100.0
    
    return {
        'rms_ratio': rms_ratio * 100,
        'std_ratio': std_ratio * 100,
        'zcr_ratio': zcr_ratio * 100,
        'peak_ratio': peak_ratio * 100,
        'crest_sim': crest_sim * 100,
        'overall': similarity
    }

def main():
    fixtures = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures/a_color_tests")
    output = Path("/home/aik/rustProjects/GensokyoDSP/tests/output")
    
    # 分析几个a_color测试
    test_names = ["a_color_0.0", "a_color_0.0547"]
    
    for test_name in test_names:
        ref_file = fixtures / f"{test_name}.wav"
        out_file = output / f"test_{test_name}.wav"
        
        if not out_file.exists():
            print(f"\n{test_name}: 输出文件不存在")
            continue
        
        ref_feat = analyze_wav(ref_file)
        out_feat = analyze_wav(out_file)
        comparison = compare_features(ref_feat, out_feat)
        
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")
        
        print(f"\n参考文件特征:")
        for k, v in ref_feat.items():
            print(f"  {k:8s}: {v:.6f}")
        
        print(f"\n输出文件特征:")
        for k, v in out_feat.items():
            print(f"  {k:8s}: {v:.6f}")
        
        print(f"\n相似度分析:")
        for k, v in comparison.items():
            print(f"  {k:12s}: {v:.2f}%")

if __name__ == "__main__":
    main()
