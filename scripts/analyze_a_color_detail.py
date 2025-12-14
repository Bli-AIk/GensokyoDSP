import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

# 比较 a_color=0.4536 的频谱
test_values = [0.4536, 0.7025, 0.9051, 1.0]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, a_color in enumerate(test_values):
    # 读取参考和测试音频
    ref_path = f'tests/fixtures/a_color_tests/a_color_{a_color}.wav'
    test_path = f'tests/output/test_a_color_{a_color}.wav'
    
    try:
        sr_ref, audio_ref = wav.read(ref_path)
        sr_test, audio_test = wav.read(test_path)
        
        # 归一化
        if audio_ref.dtype == np.int16:
            audio_ref = audio_ref.astype(np.float32) / 32768.0
        if audio_test.dtype == np.int16:
            audio_test = audio_test.astype(np.float32) / 32768.0
        
        # 取单声道
        if len(audio_ref.shape) > 1:
            audio_ref = audio_ref[:, 0]
        if len(audio_test.shape) > 1:
            audio_test = audio_test[:, 0]
        
        # 取稳定段分析 (1-6秒)
        start = int(sr_ref * 1.0)
        end = int(sr_ref * 6.0)
        audio_ref = audio_ref[start:end]
        audio_test = audio_test[start:end]
        
        # FFT分析
        fft_ref = np.fft.rfft(audio_ref)
        fft_test = np.fft.rfft(audio_test)
        
        freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)
        
        # 功率谱密度
        psd_ref = np.abs(fft_ref) ** 2
        psd_test = np.abs(fft_test) ** 2
        
        # 平滑
        from scipy.ndimage import uniform_filter1d
        psd_ref_smooth = uniform_filter1d(psd_ref, size=100)
        psd_test_smooth = uniform_filter1d(psd_test, size=100)
        
        ax = axes[idx]
        ax.loglog(freqs[1:], psd_ref_smooth[1:], label='Reference', alpha=0.7)
        ax.loglog(freqs[1:], psd_test_smooth[1:], label='Test', alpha=0.7)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Power')
        ax.set_title(f'a_color={a_color}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([20, 20000])
        
        # 计算RMS
        rms_ref = np.sqrt(np.mean(audio_ref**2))
        rms_test = np.sqrt(np.mean(audio_test**2))
        
        print(f"\na_color={a_color}:")
        print(f"  RMS: ref={rms_ref:.5f}, test={rms_test:.5f}, ratio={rms_test/rms_ref:.3f}")
        
        # 计算频谱斜率 (log-log线性回归)
        # 使用100Hz-5kHz范围
        mask_ref = (freqs > 100) & (freqs < 5000)
        log_f = np.log10(freqs[mask_ref])
        log_psd_ref = np.log10(psd_ref_smooth[mask_ref] + 1e-12)
        log_psd_test = np.log10(psd_test_smooth[mask_ref] + 1e-12)
        
        slope_ref = np.polyfit(log_f, log_psd_ref, 1)[0]
        slope_test = np.polyfit(log_f, log_psd_test, 1)[0]
        
        print(f"  Slope: ref={slope_ref:.3f}, test={slope_test:.3f}, diff={abs(slope_ref-slope_test):.3f}")
        
    except Exception as e:
        print(f"Error processing a_color={a_color}: {e}")
        axes[idx].text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=axes[idx].transAxes)

plt.tight_layout()
plt.savefig('a_color_spectrum_detail.png', dpi=150)
print("\nSaved to a_color_spectrum_detail.png")
