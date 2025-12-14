import numpy as np
import scipy.io.wavfile as wav

test_values = [0.0, 0.0547, 0.1058, 0.1496, 0.2007, 0.2518, 0.3102, 0.3540, 0.4051, 
               0.4536, 0.5506, 0.6055, 0.6519, 0.7025, 0.7489, 0.8080, 0.8502, 0.9051, 0.9515, 1.0]

print("a_color | RMS_ref | RMS_test | Ratio | Slope_ref | Slope_test | Diff")
print("-" * 80)

for a_color in test_values:
    ref_path = f'tests/fixtures/a_color_tests/a_color_{a_color}.wav'
    test_path = f'tests/output/test_a_color_{a_color}.wav'
    
    try:
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
        
        # RMS
        rms_ref = np.sqrt(np.mean(audio_ref**2))
        rms_test = np.sqrt(np.mean(audio_test**2))
        
        # FFT
        fft_ref = np.fft.rfft(audio_ref)
        fft_test = np.fft.rfft(audio_test)
        freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)
        
        psd_ref = np.abs(fft_ref) ** 2
        psd_test = np.abs(fft_test) ** 2
        
        from scipy.ndimage import uniform_filter1d
        psd_ref_smooth = uniform_filter1d(psd_ref, size=100)
        psd_test_smooth = uniform_filter1d(psd_test, size=100)
        
        # 斜率计算 (100Hz - 5kHz)
        mask = (freqs > 100) & (freqs < 5000)
        log_f = np.log10(freqs[mask])
        log_psd_ref = np.log10(psd_ref_smooth[mask] + 1e-12)
        log_psd_test = np.log10(psd_test_smooth[mask] + 1e-12)
        
        slope_ref = np.polyfit(log_f, log_psd_ref, 1)[0]
        slope_test = np.polyfit(log_f, log_psd_test, 1)[0]
        
        print(f"{a_color:6.4f} | {rms_ref:.5f} | {rms_test:.5f} | {rms_test/rms_ref:.3f} | {slope_ref:7.3f} | {slope_test:7.3f} | {abs(slope_ref-slope_test):.3f}")
        
    except Exception as e:
        print(f"{a_color:6.4f} | Error: {e}")

