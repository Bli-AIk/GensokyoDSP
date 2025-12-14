import numpy as np
import scipy.io.wavfile as wav

for a_noise in [0.8080, 0.8502]:
    ref_path = f'tests/fixtures/a_noise_tests/a_noise_{a_noise}.wav'
    test_path = f'tests/output/test_a_noise_{a_noise}.wav'
    
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
    
    print(f"\na_noise={a_noise}:")
    print(f"  RMS: ref={rms_ref:.5f}, test={rms_test:.5f}, ratio={rms_test/rms_ref:.3f}")
    print(f"  Need gain adjustment: {rms_ref/rms_test:.3f}x")
