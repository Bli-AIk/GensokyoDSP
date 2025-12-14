import numpy as np
import scipy.io.wavfile as wav

test_value = 0.8502

ref_path = f'tests/fixtures/a_noise_tests/a_noise_{test_value}.wav'
test_path = f'tests/output/test_a_noise_{test_value}.wav'

sr_ref, audio_ref = wav.read(ref_path)
sr_test, audio_test = wav.read(test_path)

if audio_ref.dtype == np.int16:
    audio_ref = audio_ref.astype(np.float32) / 32768.0
if audio_test.dtype == np.int16:
    audio_test = audio_test.astype(np.float32) / 32768.0

if len(audio_ref.shape) > 1:
    audio_ref = audio_ref[:, 0]
if len(audio_test.shape) > 1:
    audio_test = audio_test[:, 0]

start = int(sr_ref * 1.0)
end = int(sr_ref * 6.0)
audio_ref = audio_ref[start:end]
audio_test = audio_test[start:end]

rms_ref = np.sqrt(np.mean(audio_ref**2))
rms_test = np.sqrt(np.mean(audio_test**2))

fft_ref = np.fft.rfft(audio_ref)
fft_test = np.fft.rfft(audio_test)
freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)

psd_ref = np.abs(fft_ref) ** 2
psd_test = np.abs(fft_test) ** 2

from scipy.ndimage import uniform_filter1d
psd_ref_smooth = uniform_filter1d(psd_ref, size=100)
psd_test_smooth = uniform_filter1d(psd_test, size=100)

# 分析不同频段的能量
def band_energy(psd, freqs, f_low, f_high):
    mask = (freqs >= f_low) & (freqs < f_high)
    return np.sum(psd[mask])

bands = [(0, 500), (500, 2000), (2000, 5000), (5000, 10000), (10000, 20000)]
print(f"\na_noise={test_value}:")
print(f"  RMS: ref={rms_ref:.5f}, test={rms_test:.5f}, ratio={rms_test/rms_ref:.3f}")
print(f"\n  Frequency band energy:")
for f_low, f_high in bands:
    e_ref = band_energy(psd_ref, freqs, f_low, f_high)
    e_test = band_energy(psd_test, freqs, f_low, f_high)
    print(f"    {f_low:5d}-{f_high:5d}Hz: ref={e_ref:.2e}, test={e_test:.2e}, ratio={e_test/e_ref:.3f}")

# 计算频谱斜率
mask = (freqs > 100) & (freqs < 5000)
log_f = np.log10(freqs[mask])
log_psd_ref = np.log10(psd_ref_smooth[mask] + 1e-12)
log_psd_test = np.log10(psd_test_smooth[mask] + 1e-12)

slope_ref = np.polyfit(log_f, log_psd_ref, 1)[0]
slope_test = np.polyfit(log_f, log_psd_test, 1)[0]

print(f"\n  Spectral slope: ref={slope_ref:.3f}, test={slope_test:.3f}")

# 检查基频附近的能量
fund_freq = 500.0  # 从a_freq=0.5推算
fund_mask = (freqs > fund_freq - 50) & (freqs < fund_freq + 50)
fund_e_ref = np.sum(psd_ref[fund_mask])
fund_e_test = np.sum(psd_test[fund_mask])
print(f"\n  Fundamental energy (500Hz±50Hz): ref={fund_e_ref:.2e}, test={fund_e_test:.2e}, ratio={fund_e_test/fund_e_ref:.3f}")
