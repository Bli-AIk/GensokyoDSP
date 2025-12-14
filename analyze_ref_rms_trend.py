import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from pathlib import Path

osc_mix_dir = Path("tests/fixtures/osc_mix_tests")
values = []
rms_values = []

for filepath in sorted(osc_mix_dir.glob("osc_mix_*.wav")):
    val_str = filepath.stem.replace('osc_mix_', '')
    val = float(val_str)
    
    rate, data = wavfile.read(filepath)
    if len(data.shape) > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0
    
    rms = np.sqrt(np.mean(data**2))
    
    values.append(val)
    rms_values.append(rms)

plt.figure(figsize=(12, 6))
plt.plot(values, rms_values, 'o-', linewidth=2)
plt.axvline(0.79, color='r', linestyle='--', alpha=0.5, label='50/50 point')
plt.xlabel('osc_mix')
plt.ylabel('RMS')
plt.title('Reference Audio RMS vs osc_mix')
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('ref_rms_trend.png', dpi=150)

print("参考音频RMS趋势:")
for v, r in zip(values, rms_values):
    print(f"osc_mix={v:.4f}: RMS={r:.6f}")

print(f"\nRMS范围: {min(rms_values):.6f} - {max(rms_values):.6f}")
print(f"RMS增长: {(max(rms_values) / min(rms_values) - 1) * 100:.2f}%")

# 在equal-power混合下，RMS应该保持恒定
# 但实际上有轻微增长，这可能是因为：
# 1. 谐波内容增加
# 2. 或者Synplant使用了略微不同的混合曲线

print("\n注意: 参考音频的RMS随osc_mix略有增长")
print("这表明Synplant可能:")
print("1. 不是纯粹的equal-power混合")
print("2. 或者在混合时有额外的增益补偿")
