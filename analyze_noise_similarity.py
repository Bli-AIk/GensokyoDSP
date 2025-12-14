#!/usr/bin/env python3
"""分析噪声音频的相似度 - 使用更适合噪声的指标"""
import numpy as np
from scipy.io import wavfile
from scipy import signal, stats
import sys

def load_audio(filepath):
    """加载音频文件"""
    sr, data = wavfile.read(filepath)
    
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    else:
        data = data.astype(np.float64)
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    return sr, data

def compute_spectral_features(sr, data, n_bands=32):
    """计算频谱特征"""
    # 使用多个短时窗口计算平均频谱特征
    window_size = sr // 4  # 250ms窗口
    hop_size = sr // 8     # 125ms跳跃
    
    # 计算STFT
    f, t, Zxx = signal.stft(data, sr, nperseg=window_size, noverlap=window_size-hop_size)
    magnitude = np.abs(Zxx)
    
    # 将频率分成多个频段
    freq_bands = np.logspace(np.log10(20), np.log10(sr/2), n_bands+1)
    band_energies = []
    
    for i in range(n_bands):
        mask = (f >= freq_bands[i]) & (f < freq_bands[i+1])
        if np.any(mask):
            # 对每个频段，计算时间平均能量
            band_energy = np.mean(magnitude[mask, :], axis=0)
            band_energies.append(np.mean(band_energy))
        else:
            band_energies.append(0.0)
    
    return np.array(band_energies)

def compute_temporal_features(data):
    """计算时域特征"""
    # RMS
    rms = np.sqrt(np.mean(data**2))
    
    # 峰值
    peak = np.max(np.abs(data))
    
    # 波峰因数
    crest_factor = peak / (rms + 1e-10)
    
    # 零交叉率
    zero_crossings = np.sum(np.abs(np.diff(np.sign(data)))) / (2 * len(data))
    
    # 包络统计
    envelope = np.abs(signal.hilbert(data))
    env_mean = np.mean(envelope)
    env_std = np.std(envelope)
    
    return {
        'rms': rms,
        'peak': peak,
        'crest_factor': crest_factor,
        'zero_crossings': zero_crossings,
        'env_mean': env_mean,
        'env_std': env_std
    }

def compute_statistical_similarity(data1, data2):
    """计算统计相似度"""
    # 归一化到相同RMS
    rms1 = np.sqrt(np.mean(data1**2))
    rms2 = np.sqrt(np.mean(data2**2))
    
    if rms1 > 1e-10:
        data1_norm = data1 / rms1
    else:
        data1_norm = data1
    
    if rms2 > 1e-10:
        data2_norm = data2 / rms2
    else:
        data2_norm = data2
    
    # 计算直方图相似度（KL散度）
    hist1, bins = np.histogram(data1_norm, bins=100, range=(-3, 3), density=True)
    hist2, _ = np.histogram(data2_norm, bins=bins, density=True)
    
    # 避免零值
    hist1 = hist1 + 1e-10
    hist2 = hist2 + 1e-10
    hist1 = hist1 / np.sum(hist1)
    hist2 = hist2 / np.sum(hist2)
    
    # 使用对称KL散度
    kl_div = 0.5 * (np.sum(hist1 * np.log(hist1 / hist2)) + np.sum(hist2 * np.log(hist2 / hist1)))
    
    # 转换为相似度分数 (0-1)
    hist_similarity = np.exp(-kl_div)
    
    return hist_similarity

def compare_noise_audio(ref_path, gen_path):
    """对比两个噪声音频文件"""
    print(f"\n分析: {ref_path} vs {gen_path}")
    print("=" * 70)
    
    sr1, data1 = load_audio(ref_path)
    sr2, data2 = load_audio(gen_path)
    
    if sr1 != sr2:
        print(f"警告: 采样率不匹配 ({sr1} vs {sr2})")
        return None
    
    # 截取相同长度
    min_len = min(len(data1), len(data2))
    data1 = data1[:min_len]
    data2 = data2[:min_len]
    
    # 1. 计算频谱特征相似度
    spec_feat1 = compute_spectral_features(sr1, data1)
    spec_feat2 = compute_spectral_features(sr2, data2)
    
    # 归一化频谱特征
    spec_feat1_norm = spec_feat1 / (np.sum(spec_feat1) + 1e-10)
    spec_feat2_norm = spec_feat2 / (np.sum(spec_feat2) + 1e-10)
    
    # 计算余弦相似度
    spec_similarity = np.dot(spec_feat1_norm, spec_feat2_norm) / (
        np.linalg.norm(spec_feat1_norm) * np.linalg.norm(spec_feat2_norm) + 1e-10
    )
    
    # 2. 计算时域特征相似度
    temp_feat1 = compute_temporal_features(data1)
    temp_feat2 = compute_temporal_features(data2)
    
    # RMS相似度
    rms_ratio = min(temp_feat1['rms'], temp_feat2['rms']) / (max(temp_feat1['rms'], temp_feat2['rms']) + 1e-10)
    
    # 波峰因数相似度
    cf_diff = abs(temp_feat1['crest_factor'] - temp_feat2['crest_factor'])
    cf_similarity = np.exp(-cf_diff / 2.0)
    
    # 零交叉率相似度
    zcr_diff = abs(temp_feat1['zero_crossings'] - temp_feat2['zero_crossings'])
    zcr_similarity = np.exp(-zcr_diff * 10)
    
    # 3. 统计分布相似度
    stat_similarity = compute_statistical_similarity(data1, data2)
    
    # 4. 综合相似度
    # 对于噪声，频谱特征最重要
    weights = {
        'spectral': 0.50,      # 频谱分布
        'rms': 0.15,           # 能量水平
        'statistical': 0.20,   # 统计分布
        'crest_factor': 0.10,  # 波峰因数
        'zero_crossings': 0.05 # 零交叉率
    }
    
    overall_similarity = (
        weights['spectral'] * spec_similarity +
        weights['rms'] * rms_ratio +
        weights['statistical'] * stat_similarity +
        weights['crest_factor'] * cf_similarity +
        weights['zero_crossings'] * zcr_similarity
    )
    
    # 转换为百分比
    overall_similarity_percent = overall_similarity * 100
    
    print(f"\n频谱相似度: {spec_similarity * 100:.2f}%")
    print(f"RMS相似度: {rms_ratio * 100:.2f}%")
    print(f"统计分布相似度: {stat_similarity * 100:.2f}%")
    print(f"波峰因数相似度: {cf_similarity * 100:.2f}%")
    print(f"零交叉率相似度: {zcr_similarity * 100:.2f}%")
    print(f"\n综合相似度: {overall_similarity_percent:.2f}%")
    
    print(f"\nRMS: {temp_feat1['rms']:.6f} vs {temp_feat2['rms']:.6f}")
    print(f"波峰因数: {temp_feat1['crest_factor']:.3f} vs {temp_feat2['crest_factor']:.3f}")
    print(f"零交叉率: {temp_feat1['zero_crossings']:.6f} vs {temp_feat2['zero_crossings']:.6f}")
    
    return {
        'spectral': spec_similarity,
        'rms': rms_ratio,
        'statistical': stat_similarity,
        'crest_factor': cf_similarity,
        'zero_crossings': zcr_similarity,
        'overall': overall_similarity_percent
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 分析指定的噪声值
        noise_val = sys.argv[1]
        ref_file = f"tests/fixtures/a_noise_tests/a_noise_{noise_val}.wav"
        gen_file = f"tests/output/test_a_noise_{noise_val}.wav"
        compare_noise_audio(ref_file, gen_file)
    else:
        # 分析所有失败的测试
        failed_vals = ["0.5506", "0.6055", "0.6519", "0.7025", "0.7489", 
                       "0.8080", "0.8502", "0.9051", "0.9515", "1.0"]
        
        results = []
        for val in failed_vals:
            ref_file = f"tests/fixtures/a_noise_tests/a_noise_{val}.wav"
            gen_file = f"tests/output/test_a_noise_{val}.wav"
            result = compare_noise_audio(ref_file, gen_file)
            if result:
                results.append((val, result))
        
        print("\n\n总结:")
        print("=" * 70)
        print(f"{'噪声值':>8} | {'频谱':>6} | {'RMS':>6} | {'统计':>6} | {'综合':>6}")
        print("-" * 70)
        for val, res in results:
            print(f"{val:>8} | {res['spectral']*100:>6.2f} | {res['rms']*100:>6.2f} | "
                  f"{res['statistical']*100:>6.2f} | {res['overall']:>6.2f}")
