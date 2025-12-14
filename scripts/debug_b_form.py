
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os

def analyze_audio(file_path):
    data, samplerate = sf.read(file_path)
    if len(data.shape) > 1:
        data = data[:, 0] # Take first channel
    return data, samplerate

def plot_comparison(ref_file, gen_file, output_image):
    ref_data, ref_sr = analyze_audio(ref_file)
    gen_data, gen_sr = analyze_audio(gen_file)

    # Ensure same length
    min_len = min(len(ref_data), len(gen_data))
    ref_data = ref_data[:min_len]
    gen_data = gen_data[:min_len]
    
    time = np.arange(min_len) / ref_sr

    plt.figure(figsize=(15, 10))

    # Plot Waveform
    plt.subplot(3, 1, 1)
    plt.plot(time, ref_data, label='Reference', alpha=0.7)
    plt.plot(time, gen_data, label='Generated', alpha=0.7)
    plt.title('Waveform Comparison')
    plt.legend()
    plt.grid(True)

    # Plot Spectrum
    plt.subplot(3, 1, 2)
    ref_fft = np.fft.rfft(ref_data)
    gen_fft = np.fft.rfft(gen_data)
    freq = np.fft.rfftfreq(min_len, 1/ref_sr)
    
    plt.plot(freq, 20 * np.log10(np.abs(ref_fft) + 1e-6), label='Reference')
    plt.plot(freq, 20 * np.log10(np.abs(gen_fft) + 1e-6), label='Generated', alpha=0.7)
    plt.xscale('log')
    plt.title('Frequency Spectrum (dB)')
    plt.legend()
    plt.grid(True)

    # Plot detailed waveform (zoom in)
    plt.subplot(3, 1, 3)
    zoom_samples = 1000
    start_sample = len(ref_data) // 2
    end_sample = start_sample + zoom_samples
    plt.plot(time[start_sample:end_sample], ref_data[start_sample:end_sample], label='Reference')
    plt.plot(time[start_sample:end_sample], gen_data[start_sample:end_sample], label='Generated')
    plt.title(f'Waveform Zoom (Samples {start_sample}-{end_sample})')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_image)
    print(f"Analysis saved to {output_image}")
    
    # Print statistics
    print(f"Reference RMS: {np.sqrt(np.mean(ref_data**2)):.6f}")
    print(f"Generated RMS: {np.sqrt(np.mean(gen_data**2)):.6f}")
    print(f"Max Ref: {np.max(np.abs(ref_data)):.6f}")
    print(f"Max Gen: {np.max(np.abs(gen_data)):.6f}")
    
    # Peak Frequency
    ref_peak_idx = np.argmax(np.abs(ref_fft))
    gen_peak_idx = np.argmax(np.abs(gen_fft))
    ref_peak_freq = freq[ref_peak_idx]
    gen_peak_freq = freq[gen_peak_idx]
    print(f"Ref Peak Frequency: {ref_peak_freq:.2f} Hz")
    print(f"Gen Peak Frequency: {gen_peak_freq:.2f} Hz")

if __name__ == "__main__":
    ref_path = "tests/fixtures/b_form_tests/b_form_0.5506.wav"
    gen_path = "tests/output/test_b_form_0.5506.wav"
    
    if os.path.exists(ref_path) and os.path.exists(gen_path):
        plot_comparison(ref_path, gen_path, "b_form_debug.png")
    else:
        print(f"Files not found: {ref_path} or {gen_path}")
