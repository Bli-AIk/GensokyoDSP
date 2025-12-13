use crate::synplant::SynplantGenome;
use fundsp::hacker::*;
use std::f64::consts::PI;

/// Target RMS values (measured from reference audio)
static TARGET_RMS_TABLE: &[(f64, f64)] = &[
    (0.00, 0.063), (0.05, 0.063014), (0.10, 0.056808), (0.15, 0.063015),
    (0.20, 0.056811), (0.25, 0.063021), (0.30, 0.056822), (0.35, 0.063041),
    (0.40, 0.056850), (0.45, 0.063094), (0.50, 0.056965), (0.55, 0.063219),
    (0.60, 0.058848), (0.65, 0.064342), (0.70, 0.057971), (0.75, 0.065266),
    (0.80, 0.059344), (0.85, 0.066154), (0.90, 0.061865), (0.95, 0.047197), 
    (1.00, 0.030622),
];

/// Estimated RMS values (theoretical/calculated)
static ESTIMATED_RMS_TABLE: &[(f64, f64)] = &[
    (0.00, 0.707), (0.05, 0.704), (0.10, 0.696), (0.15, 0.684),
    (0.20, 0.670), (0.25, 0.653), (0.30, 0.634), (0.35, 0.615),
    (0.40, 0.597), (0.45, 0.580), (0.50, 0.566), (0.55, 0.558),
    (0.57, 0.506), (0.60, 0.505), (0.65, 0.502), (0.70, 0.498),
    (0.75, 0.493), (0.80, 0.488), (0.85, 0.464), (0.90, 0.340), 
    (0.95, 0.152), (1.00, 0.065),
];

/// 线性插值辅助函数
fn interpolate(points: &[(f64, f64)], x: f64) -> f64 {
    // 边界情况
    if x <= points[0].0 {
        return points[0].1;
    }
    if x >= points[points.len() - 1].0 {
        return points[points.len() - 1].1;
    }
    
    // 查找插值区间
    for i in 0..points.len() - 1 {
        if x >= points[i].0 && x <= points[i + 1].0 {
            let x0 = points[i].0;
            let x1 = points[i + 1].0;
            let y0 = points[i].1;
            let y1 = points[i + 1].1;
            
            // 线性插值
            let t = (x - x0) / (x1 - x0);
            return y0 + t * (y1 - y0);
        }
    }
    
    points[0].1 // 默认返回
}

/// RMS Compensator Node
/// Input: Form (0.0 - 1.0)
/// Output: Gain adjustment factor
#[derive(Clone)]
struct RmsCompensator;

impl AudioNode for RmsCompensator {
    const ID: u64 = 92;
    type Inputs = U1;
    type Outputs = U1;

    fn tick(&mut self, input: &Frame<f32, Self::Inputs>) -> Frame<f32, Self::Outputs> {
        let form = input[0] as f64;
        let target_rms = interpolate(TARGET_RMS_TABLE, form);
        let estimated_rms = interpolate(ESTIMATED_RMS_TABLE, form);
        let gain = (target_rms / estimated_rms) as f32;
        [gain].into()
    }
}

/// 自定义波形变形振荡器
/// Inputs: Frequency (Hz), Form (0.0 - 1.0)
/// Output: Waveform Sample
#[derive(Clone)]
struct MorphOscillator {
    phase: f64,
    sample_rate: f64,
}

impl MorphOscillator {
    fn new(sample_rate: f64) -> Self {
        Self {
            phase: 0.0,
            sample_rate,
        }
    }
    
    fn tick_sample(&mut self, freq: f32, form: f32) -> f32 {
        let output = Self::morph_waveform(self.phase, form as f64);
        
        // 更新相位
        self.phase += freq as f64 / self.sample_rate;
        if self.phase >= 1.0 {
            self.phase -= 1.0;
        }
        
        output as f32
    }
    
    /// 生成带限锯齿波
    fn generate_saw(phase: f64, rolloff_strength: f64) -> f64 {
        Self::generate_saw_custom(phase, 64, rolloff_strength)
    }

    /// 生成单个采样点的波形值
    fn morph_waveform(phase: f64, form: f64) -> f64 {
        let form = form.clamp(0.0, 1.0);
        let p = phase;
        
        if form < 0.57 {
            // 阶段1: 正弦波 -> 锯齿波 (0.0 到 0.57)
            let t = form / 0.57;
            
            let sine = (p * 2.0 * PI).sin();
            let saw = Self::generate_saw(p, 20.0);
            
            let blend = t.powf(1.8);
            sine * (1.0 - blend) + saw * blend
            
        } else if form < 0.8 {
            // 阶段2: 锯齿波 -> 方波 (0.57 到 0.8)
            // 使用 (1 - 0.5k)Saw(p) - 0.5k*Saw(p-0.5) 公式
            
            let even_odd_ratio = if form < 0.6 {
                1.0 - (form - 0.57) / (0.6 - 0.57) * (1.0 - 0.85)
            } else if form < 0.65 {
                0.85 - (form - 0.6) / (0.65 - 0.6) * (0.85 - 0.65)
            } else if form < 0.7 {
                0.65 - (form - 0.65) / (0.7 - 0.65) * (0.65 - 0.45)
            } else if form < 0.75 {
                0.45 - (form - 0.7) / (0.75 - 0.7) * (0.45 - 0.20)
            } else {
                0.20 - (form - 0.75) / (0.8 - 0.75) * 0.20
            };
            
            let k = 1.0 - even_odd_ratio;
            
            let rolloff_strength = if form >= 0.64 && form <= 0.71 { 35.0 } 
                                   else if form >= 0.6 && form <= 0.77 { 28.0 } 
                                   else { 20.0 };
            
            let saw_p = Self::generate_saw(p, rolloff_strength);
            let saw_shifted = Self::generate_saw(p - 0.5, rolloff_strength);
            
            // Phase 2: Saw (O+E) -> Square (O)
            // Target = Odd + ratio * Even
            // Odd = 0.5 * (S - S')
            // Even = 0.5 * (S + S')
            // Target = 0.5 * [ (1+ratio)S - (1-ratio)S' ]
            
            0.5 * ( (1.0 + even_odd_ratio) * saw_p - (1.0 - even_odd_ratio) * saw_shifted )
            
        } else {
            // 阶段3: 方波 -> 脉冲波 (0.8 到 1.0)
            // 使用 0.5 * (Saw(p) - Saw(p - d)) 公式
            
            let duty_cycle = if form <= 0.85 {
                0.500 + (form - 0.8) / (0.85 - 0.8) * (0.652 - 0.500)
            } else if form <= 0.9 {
                0.652 + (form - 0.85) / (0.9 - 0.85) * (0.850 - 0.652) 
            } else if form <= 0.95 {
                0.850 + (form - 0.9) / (0.95 - 0.9) * (0.970 - 0.850)
            } else {
                0.970 + (form - 0.95) / (1.0 - 0.95) * (0.985 - 0.970)
            };
            
            let rolloff_strength = if duty_cycle > 0.97 { 15.0 } 
                                   else if duty_cycle > 0.94 { 25.0 } 
                                   else if duty_cycle > 0.93 { 30.0 } 
                                   else if duty_cycle > 0.9 { 35.0 } 
                                   else { 20.0 };
            
            // Phase 3: Square (O) -> Pulse
            // Must match Phase 2 end: 0.5 * (S(p) - S(p-0.5))
            // Formula: 0.5 * (Saw(p - 0.5 - d) - Saw(p - 0.5))
            // When d=0.5: 0.5 * (S(p-1) - S(p-0.5)) = 0.5 * (S(p) - S(p-0.5)) -> Matches Square
            // When d=1.0: 0.5 * (S(p-1.5) - S(p-0.5)) = 0 -> Matches Pulse width 0
            
            // We need custom generate_saw to support variable max_harmonics if needed, 
            // but for now generate_saw (64 harmonics) is consistent with Phase 2.
            // However, Phase 3 needs more harmonics for sharpness.
            
            let max_harmonics = if duty_cycle > 0.97 { 512 } 
                                else if duty_cycle > 0.94 { 384 } 
                                else if duty_cycle > 0.93 { 256 } 
                                else if duty_cycle > 0.9 { 128 } 
                                else { 64 };
                                
            let saw_base = Self::generate_saw_custom(p - 0.5, max_harmonics, rolloff_strength);
            let saw_mod = Self::generate_saw_custom(p - 0.5 - duty_cycle, max_harmonics, rolloff_strength);
            
            0.5 * (saw_mod - saw_base)
        }
    }
    
    // Removed unused generate_pwm_from_saw helper
    
    fn generate_saw_custom(phase: f64, max_harmonics: i32, rolloff_strength: f64) -> f64 {
        let mut saw = 0.0;
        for n in 1..=max_harmonics {
            let n_f = n as f64;
            let amp = (-1.0_f64).powi(n + 1) / n_f;
            let rolloff = 1.0 / (1.0 + (n_f / rolloff_strength).powi(2));
            saw += amp * (phase * 2.0 * PI * n_f).sin() * rolloff;
        }
        saw * (2.0 / PI)
    }
}

impl AudioNode for MorphOscillator {
    const ID: u64 = 91;
    type Inputs = U2;
    type Outputs = U1;
    
    fn tick(&mut self, input: &Frame<f32, Self::Inputs>) -> Frame<f32, Self::Outputs> {
        [self.tick_sample(input[0], input[1])].into()
    }
    
    fn set_sample_rate(&mut self, sample_rate: f64) {
        self.sample_rate = sample_rate;
    }
}

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
        let attack_time = 0.01; 
        let sustain_level = self.genome.vol_sus as f64;
        
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
    
    pub fn synthesize_with_params(&self, duration: f64, sample_rate: f64) -> Wave {
        let freq_a = self.calculate_frequency(self.genome.a_freq);
        let form_a = self.genome.a_form;
        
        let osc_node = self.create_oscillator_node(sample_rate);
        let comp_node = self.create_compensator_node();
        
        let form_sig_1 = constant(form_a);
        let form_sig_2 = constant(form_a);
        let freq_sig = constant(freq_a);
        
        let source = (freq_sig | form_sig_1) >> osc_node;
        let compensation = form_sig_2 >> comp_node;
        let osc_a = source * compensation;
        
        let volume_env = self.create_envelope_node();
        let with_envelope = osc_a * volume_env;
        
        let cutoff = if self.genome.flt_freq >= 0.99 {
            20000.0  // 全开
        } else {
            let min_cutoff = freq_a;
            let max_cutoff = 20000.0;
            min_cutoff * (max_cutoff / min_cutoff).powf(self.genome.flt_freq)
        };
        let filtered = with_envelope >> lowpass_hz(cutoff, 1.0);
        
        let mut graph = filtered >> split::<U2>();
        
        Wave::render(sample_rate, duration, &mut graph)
    }
    
    /// 用于测试的动态合成接口
    pub fn synthesize_dynamic_test<F>(&self, duration: f64, sample_rate: f64, freq: f32, form_generator: F) -> Wave 
    where F: Fn(f64) -> f64 + Clone + Send + Sync + 'static 
    {
        let osc_node = self.create_oscillator_node(sample_rate);
        let comp_node = self.create_compensator_node();
        
        let freq_sig = constant(freq);
        let form_sig_1 = lfo(form_generator.clone());
        let form_sig_2 = lfo(form_generator);
        
        let source = (freq_sig | form_sig_1) >> osc_node;
        let compensation = form_sig_2 >> comp_node;
        let osc_a = source * compensation;
        
        let attack_time = 0.15;
        let volume_env = envelope(move |t| {
            if t < attack_time {
                t / attack_time
            } else {
                1.0
            }
        });
        let with_envelope = osc_a * volume_env;
        
        let cutoff = if self.genome.flt_freq >= 0.99 {
            20000.0 
        } else {
            let min_cutoff = freq; 
            let max_cutoff = 20000.0;
            min_cutoff * (max_cutoff / min_cutoff).powf(self.genome.flt_freq)
        };
        let filtered = with_envelope >> lowpass_hz(cutoff, 1.0);

        let mut graph = filtered >> split::<U2>();
        Wave::render(sample_rate, duration, &mut graph)
    }
    
    pub fn synthesize(&self, duration: f64) -> Wave {
        self.synthesize_with_params(duration, 48000.0)
    }
}
