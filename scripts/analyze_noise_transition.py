import numpy as np
import scipy.io.wavfile as wav

test_values = [0.7025, 0.7489, 0.8080, 0.8502, 0.9051, 0.9515]

print("a_noise |  RMS_ref | RMS_test | Ratio | Low_band | Mid_band | High_band")
print("-" * 80)

for a_noise in test_values:
    ref_path = f'tests/fixtures/a_noise_tests/a_noise_{a_noise}.wav'
    test_path = f'tests/output/test_a_noise_{a_noise}.wav'
    
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
        
        rms_ref = np.sqrt(np.mean(audio_ref**2))
        rms_test = np.sqrt(np.mean(audio_test**2))
        
        # FFT
        fft_ref = np.fft.rfft(audio_ref)
        fft_test = np.fft.rfft(audio_test)
        freqs = np.fft.rfftfreq(len(audio_ref), 1/sr_ref)
        
        psd_ref = np.abs(fft_ref) ** 2
        psd_test = np.abs(fft_test) ** 2
        
        # 能量分布
        def band_energy(psd, freqs, f_low, f_high):
            mask = (freqs >= f_low) & (freqs < f_high)
            return np.sum(psd[mask])
        
        low_ref = band_energy(psd_ref, freqs, 0, 1000)
        mid_ref = band_energy(psd_ref, freqs, 1000, 5000)
        high_ref = band_energy(psd_ref, freqs, 5000, 15000)
        
        low_test = band_energy(psd_test, freqs, 0, 1000)
        mid_test = band_energy(psd_test, freqs, 1000, 5000)
        high_test = band_energy(psd_test, freqs, 5000, 15000)
        
        print(f"{a_noise:7.4f} | {rms_ref:8.5f} | {rms_test:8.5f} | {rms_test/rms_ref:5.2f} | {low_test/low_ref:8.2f} | {mid_test/mid_ref:8.2f} | {high_test/high_ref:8.2f}")
        
    except Exception as e:
        print(f"{a_noise:7.4f} | Error: {e}")

