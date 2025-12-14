use crate::dsp::compensator::RmsCompensator;
use crate::dsp::oscillator::MorphOscillator;
use crate::synplant::SynplantGenome;
use fundsp::hacker::*;

pub struct SynplantSynthesizer {
    genome: SynplantGenome,
}

impl SynplantSynthesizer {
    pub fn new(genome: SynplantGenome) -> Self {
        Self { genome }
    }

    /// 将频率参数 (0.0-1.0) 转换为实际频率 (Hz)
    fn calculate_frequency(&self, freq_param: f32) -> f32 {
        let midi_note = 72.0 + (freq_param - 0.5) * 48.0;
        // TODO: Add modulation (LFO, Envelope) to pitch
        // TODO: Handle 'mod_kf' (keyboard follow) if applicable
        440.0 * 2_f32.powf((midi_note - 69.0) / 12.0)
    }

    /// 创建振荡器节点
    fn create_oscillator_node(&self, sample_rate: f64) -> An<MorphOscillator> {
        An(MorphOscillator::new(sample_rate))
    }

    /// 创建补偿节点
    fn create_compensator_node(&self) -> An<RmsCompensator> {
        An(RmsCompensator)
    }

    /// 创建默认的音量包络节点
    fn create_envelope_node(&self) -> An<impl AudioNode<Inputs = U0, Outputs = U1>> {
        let vol_atk = self.genome.vol_atk as f64;
        let sustain_level = self.genome.vol_sus as f64;
        // TODO: Implement full ADSR envelope (Decay, Release/Fade)
        // TODO: Implement envelope looping if env_loop > 0

        // For now, simple Attack-Sustain
        let attack_time = 0.01;

        envelope(move |t| {
            if t < attack_time {
                let progress = t / attack_time;
                if vol_atk < 0.5 {
                    let curve = 2.0 - vol_atk * 4.0;
                    progress.powf(curve.max(1.0))
                } else {
                    let curve = (vol_atk - 0.5) * 4.0 + 1.0;
                    progress.powf(1.0 / curve)
                }
            } else {
                sustain_level
            }
        })
    }

    /// 构建滤波器部分
    fn build_filter_node(&self, freq: f32) -> An<impl AudioNode<Inputs = U1, Outputs = U1>> {
        // TODO: Implement different filter types based on `flt_type`
        // TODO: Implement resonance (Q) based on `flt_q`
        // TODO: Implement filter envelope modulation

        let cutoff = if self.genome.flt_freq >= 0.99 {
            20000.0 // 全开
        } else {
            let min_cutoff = freq;
            let max_cutoff = 20000.0;
            // Simple mapping for now
            min_cutoff * (max_cutoff / min_cutoff).powf(self.genome.flt_freq)
        };

        // Using a simple lowpass for now
        lowpass_hz(cutoff, 1.0)
    }

    pub fn synthesize_with_params(&self, duration: f64, sample_rate: f64) -> Wave {
        let freq_a = self.calculate_frequency(self.genome.a_freq);
        let form_a = self.genome.a_form;

        // TODO: Implement Oscillator B (genome.b_form, b_freq, etc.)
        // TODO: Implement Noise (genome.a_noise, b_noise)
        // TODO: Implement FM (genome.fm_amt, fm_mod)
        // TODO: Implement Ring Mod / Mix (genome.mix_mod, osc_mix)

        // Stage 1: Oscillator A
        let osc_node = self.create_oscillator_node(sample_rate);
        let comp_node = self.create_compensator_node();

        let form_sig_1 = constant(form_a);
        let form_sig_2 = constant(form_a);
        let freq_sig = constant(freq_a);

        // Osc = Freq | Form >> MorphOsc
        // Comp = Form >> RmsComp
        // Result = Osc * Comp
        let source = (freq_sig | form_sig_1) >> osc_node;
        let compensation = form_sig_2 >> comp_node;
        let osc_a = source * compensation;

        // Stage 2: Envelope
        let volume_env = self.create_envelope_node();
        let with_envelope = osc_a * volume_env;

        // Stage 3: Filter
        let filter_node = self.build_filter_node(freq_a);
        let filtered = with_envelope >> filter_node;

        // TODO: Implement Effects (Saturate, Reverb, EQ, Pan)

        let mut graph = filtered >> split::<U2>();

        Wave::render(sample_rate, duration, &mut graph)
    }

    /// 用于测试的动态合成接口
    pub fn synthesize_dynamic_test<F>(
        &self,
        duration: f64,
        sample_rate: f64,
        freq: f32,
        form_generator: F,
    ) -> Wave
    where
        F: Fn(f64) -> f64 + Clone + Send + Sync + 'static,
    {
        let osc_node = self.create_oscillator_node(sample_rate);
        let comp_node = self.create_compensator_node();

        let freq_sig = constant(freq);
        let form_sig_1 = lfo(form_generator.clone());
        let form_sig_2 = lfo(form_generator);

        let source = (freq_sig | form_sig_1) >> osc_node;
        let compensation = form_sig_2 >> comp_node;
        let osc_a = source * compensation;

        // Use the same envelope logic as main synthesis
        let volume_env = self.create_envelope_node();
        let with_envelope = osc_a * volume_env;

        // Use the same filter logic
        let filter_node = self.build_filter_node(freq);
        let filtered = with_envelope >> filter_node;

        let mut graph = filtered >> split::<U2>();
        Wave::render(sample_rate, duration, &mut graph)
    }

    pub fn synthesize(&self, duration: f64) -> Wave {
        self.synthesize_with_params(duration, 48000.0)
    }
}
