import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from pathlib import Path

# 读取音频文件
def analyze_osc_mix_audio(filepath):
    rate, data = wavfile.read(filepath)
    
    # 如果是立体声，取左声道
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 转换为浮点数
    data = data.astype(np.float32) / 32768.0
    
    # 计算RMS
    rms = np.sqrt(np.mean(data**2))
    
    # 频谱分析
    fft = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1/rate)
    magnitude = np.abs(fft)
    
    # 找到峰值频率
    peak_idx = np.argmax(magnitude[10:1000]) + 10
    peak_freq = freqs[peak_idx]
    
    return {
        'rms': rms,
        'peak_freq': peak_freq,
        'rate': rate,
        'data': data[:48000],  # 只取前1秒用于绘图
        'freqs': freqs,
        'magnitude': magnitude
    }

# 分析所有osc_mix文件
osc_mix_dir = Path("tests/fixtures/osc_mix_tests")
results = {}

for wav_file in sorted(osc_mix_dir.glob("osc_mix_*.wav")):
    value_str = wav_file.stem.replace("osc_mix_", "")
    value = float(value_str)
    
    result = analyze_osc_mix_audio(wav_file)
    results[value] = result
    
    print(f"osc_mix={value_str}: RMS={result['rms']:.6f}, Peak Freq={result['peak_freq']:.2f} Hz")

# 绘制RMS变化
values = sorted(results.keys())
rms_values = [results[v]['rms'] for v in values]

plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(values, rms_values, 'o-')
plt.xlabel('osc_mix')
plt.ylabel('RMS')
plt.title('RMS vs osc_mix')
plt.grid(True)

# 绘制峰值频率变化
peak_freqs = [results[v]['peak_freq'] for v in values]
plt.subplot(3, 1, 2)
plt.plot(values, peak_freqs, 'o-')
plt.xlabel('osc_mix')
plt.ylabel('Peak Frequency (Hz)')
plt.title('Peak Frequency vs osc_mix')
plt.grid(True)

# 绘制前4个和后4个的波形对比
plt.subplot(3, 1, 3)
for i, val in enumerate([0.0547, 0.1058, 0.9051, 1.0]):
    if val in results:
        data = results[val]['data'][:4800]  # 0.1秒
        t = np.arange(len(data)) / results[val]['rate']
        plt.plot(t, data + i*0.5, label=f'osc_mix={val}', alpha=0.7)

plt.xlabel('Time (s)')
plt.ylabel('Amplitude (offset)')
plt.title('Waveform Comparison')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('osc_mix_analysis.png', dpi=150)
print("\n分析图表已保存到 osc_mix_analysis.png")

# 详细分析b_freq（默认0.6875）的影响
print("\n根据b_freq=0.6875计算振荡器B的频率:")
a_freq = 0.5  # default
midi_a = 72.0 + (a_freq - 0.5) * 48.0
freq_a = 440.0 * 2**((midi_a - 69.0) / 12.0)
print(f"振荡器A频率 (a_freq=0.5): {freq_a:.2f} Hz")

b_freq = 0.6875
# b_freq应该控制相对音高
midi_b = 72.0 + (b_freq - 0.5) * 48.0
freq_b = 440.0 * 2**((midi_b - 69.0) / 12.0)
print(f"振荡器B频率 (b_freq=0.6875): {freq_b:.2f} Hz")
print(f"频率比: {freq_b/freq_a:.4f}")

# 查看前几个样本的频率
print("\n前5个样本的峰值频率:")
for val in sorted(results.keys())[:5]:
    print(f"  osc_mix={val:.4f}: {results[val]['peak_freq']:.2f} Hz")
    
print("\n后5个样本的峰值频率:")
for val in sorted(results.keys())[-5:]:
    print(f"  osc_mix={val:.4f}: {results[val]['peak_freq']:.2f} Hz")
