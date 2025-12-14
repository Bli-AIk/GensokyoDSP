import numpy as np
import scipy.io.wavfile as wavfile

def analyze_detailed(ref_file, test_file):
    rate_ref, data_ref = wavfile.read(ref_file)
    rate_test, data_test = wavfile.read(test_file)
    
    if len(data_ref.shape) > 1:
        data_ref = data_ref[:, 0]
    if len(data_test.shape) > 1:
        data_test = data_test[:, 0]
    
    data_ref = data_ref.astype(np.float32) / 32768.0
    data_test = data_test.astype(np.float32) / 32768.0
    
    # 计算各种指标
    rms_ref = np.sqrt(np.mean(data_ref**2))
    rms_test = np.sqrt(np.mean(data_test**2))
    
    # 波形相关性
    min_len = min(len(data_ref), len(data_test))
    corr = np.corrcoef(data_ref[:min_len], data_test[:min_len])[0, 1]
    
    # 频谱分析
    window_size = min(rate_ref, len(data_ref))
    window = np.hanning(window_size)
    
    fft_ref = np.fft.rfft(data_ref[:window_size] * window)
    fft_test = np.fft.rfft(data_test[:window_size] * window)
    
    mag_ref = np.abs(fft_ref)
    mag_test = np.abs(fft_test)
    
    # 频谱相关性
    spec_corr = np.corrcoef(mag_ref[:2000], mag_test[:2000])[0, 1]
    
    return {
        'rms_ref': rms_ref,
        'rms_test': rms_test,
        'rms_ratio': rms_test / rms_ref,
        'wave_corr': corr,
        'spec_corr': spec_corr
    }

# 分析所有测试样本
from pathlib import Path

results = []
for val in [0.0547, 0.1058, 0.2007, 0.3102, 0.4051, 0.5506, 
            0.6055, 0.7025, 0.7489, 0.8080, 0.8502, 0.9051, 0.9515, 1.0]:
    ref_file = f'tests/fixtures/osc_mix_tests/osc_mix_{val:.4f}.wav' if val != 1.0 else \
               f'tests/fixtures/osc_mix_tests/osc_mix_1.0.wav'
    test_file = f'tests/output/test_osc_mix_{val:.4f}.wav' if val != 1.0 else \
                f'tests/output/test_osc_mix_1.0.wav'
    
    if not Path(ref_file).exists() or not Path(test_file).exists():
        continue
    
    result = analyze_detailed(ref_file, test_file)
    result['osc_mix'] = val
    results.append(result)

print(f"{'osc_mix':<10} {'RMS参考':<12} {'RMS测试':<12} {'RMS比':<10} {'波形相关':<12} {'频谱相关':<12}")
print("-" * 75)

for r in results:
    print(f"{r['osc_mix']:<10.4f} {r['rms_ref']:<12.6f} {r['rms_test']:<12.6f} "
          f"{r['rms_ratio']:<10.4f} {r['wave_corr']:<12.6f} {r['spec_corr']:<12.6f}")

# 找出异常值
print("\n异常样本分析:")
for r in results:
    if r['osc_mix'] in [0.8080, 0.8502]:
        print(f"\nosc_mix={r['osc_mix']:.4f}:")
        print(f"  RMS比: {r['rms_ratio']:.4f} (应接近1.0)")
        print(f"  波形相关: {r['wave_corr']:.4f}")
        print(f"  频谱相关: {r['spec_corr']:.4f}")
        
        # 预期的osc_mix权重
        val = r['osc_mix']
        if val <= 0.79:
            angle = (val / 0.79) * (np.pi / 4)
        else:
            angle = (np.pi / 4) + ((val - 0.79) / (1.0 - 0.79)) * (np.pi / 4)
        wa = np.cos(angle)
        wb = np.sin(angle)
        print(f"  预期权重: A={wa:.4f}, B={wb:.4f}")
