use crate::dsp::colored_noise::ColoredNoise;
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
        crate::dsp::envelope::create_envelope(
            self.genome.vol_atk,
            self.genome.vol_dcy,
            self.genome.vol_sus,
            self.genome.env_time,
            self.genome.vol_fade,
        )
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
        let noise_a = self.genome.a_noise;
        let color_a = self.genome.a_color;

        // TODO: Implement Oscillator B (genome.b_form, b_freq, etc.)
        // TODO: Implement FM (genome.fm_amt, fm_mod)
        // TODO: Implement Ring Mod / Mix (genome.mix_mod, osc_mix)

        // Stage 1: Oscillator A with noise mixing
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
        let osc_pure = source * compensation;

        // Mix with colored noise
        // Key insight from a_color analysis:
        // - a_color controls noise spectrum from brown (0.0) to white (1.0)
        // - At low a_noise: narrow-band filtered noise around fundamental
        // - At high a_noise: broadband colored noise

        // Create colored noise sources
        let noise_narrow = An(ColoredNoise::new(123456789, color_a));
        let noise_broad = An(ColoredNoise::new(987654321, color_a));

        // For low a_noise: apply narrow bandpass filter to concentrate energy around fundamental
        // Q=60 creates ~200Hz bandwidth at 500Hz
        let q_narrow = 60.0;
        let filtered_narrow = noise_narrow >> bandpass_hz(freq_a, q_narrow);

        // For high a_noise: use colored noise directly (no additional filtering)
        // The ColoredNoise generator already shapes the spectrum based on a_color
        let colored_broad = noise_broad;

        let osc_weight = 1.0 - noise_a;

        // Mixing weights calibrated for correct RMS levels
        let (narrow_weight, broad_weight) = if noise_a < 0.35 {
            // Low noise: narrow-band filtered colored noise
            (noise_a * 0.022, 0.0)
        } else if noise_a < 0.74 {
            // Mid noise: gradually increase narrow-band
            let t = (noise_a - 0.35) / 0.39;
            let narrow_w = 0.0077 + t * (0.044 - 0.0077);
            (narrow_w, 0.0)
        } else if noise_a < 0.95 {
            // Transition: from narrow filtered to broad colored
            // 从0.74开始过渡
            let transition = (noise_a - 0.74) / 0.21;
            // narrow在过渡区快速降低
            let narrow_w = 0.044 * (1.0 - transition).powf(2.5);
            // broad权重：中间需要高（0.85附近），但结尾要降到0.072以匹配a_color测试
            // 使用抛物线：在transition=0.52(a_noise=0.85)处达到峰值
            let peak_transition = 0.52;
            let peak_weight = 0.115;
            let end_weight = 0.072;
            let broad_w = if transition < peak_transition {
                // 0到peak：线性增长到峰值
                peak_weight * (transition / peak_transition)
            } else {
                // peak到1：降到end_weight
                peak_weight + (end_weight - peak_weight) * ((transition - peak_transition) / (1.0 - peak_transition))
            };
            (narrow_w, broad_w)
        } else {
            // High noise: broadband colored noise dominates
            let broad_w = 0.072 + (noise_a - 0.95) * 0.028;
            (0.0, broad_w)
        };

        let osc_a = osc_pure * dc(osc_weight)
            + filtered_narrow * dc(narrow_weight)
            + colored_broad * dc(broad_weight);

        // Stage 2: Envelope
        let volume_env = self.create_envelope_node();
        let with_envelope = osc_a * volume_env;

        // Stage 3: Filter
        let filter_node = self.build_filter_node(freq_a);
        let filtered = with_envelope >> filter_node;

        // TODO: Implement Effects (Saturate, Reverb, EQ, Pan)

        // Global gain adjustment to match reference amplitude
        // Empirically determined: our output is about 70% of reference
        let gain_adjusted = filtered * dc(1.42);

        let mut graph = gain_adjusted >> split::<U2>();

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
