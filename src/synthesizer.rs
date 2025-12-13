use crate::synplant::SynplantGenome;
use fundsp::hacker::*;

pub struct SynplantSynthesizer {
    genome: SynplantGenome,
}

impl SynplantSynthesizer {
    pub fn new(genome: SynplantGenome) -> Self {
        Self { genome }
    }
    
    fn calculate_frequency(&self, _base_freq: f32, freq_param: f32) -> f32 {
        // 将0-1的参数映射到合理的频率范围 (MIDI note 21-108)
        let midi_note = 21.0 + freq_param * 87.0;
        let freq = 440.0 * 2_f32.powf((midi_note - 69.0) / 12.0);
        freq
    }
    
    pub fn synthesize(&self, duration: f64, sample_rate: f64) -> Wave {
        // 计算振荡器频率
        let freq_a = self.calculate_frequency(440.0, self.genome.a_freq);
        let freq_b = freq_a * (0.5 + self.genome.b_freq);
        
        // 使用锯齿波作为主要波形 (因为它音色丰富且适合滤波)
        let osc_a = saw_hz(freq_a);
        let osc_b = saw_hz(freq_b);
        
        // 添加噪声并混合振荡器
        let mix = self.genome.osc_mix;
        let noise_a = self.genome.a_noise;
        let noise_b = self.genome.b_noise;
        
        let mixed = (osc_a * (1.0 - noise_a) + noise() * noise_a) * (1.0 - mix)
                  + (osc_b * (1.0 - noise_b) + noise() * noise_b) * mix;
        
        // 创建包络
        let attack_time = (self.genome.vol_atk * 2.0).min(2.0) as f64;
        let decay_time = ((1.0 - self.genome.vol_dcy) * 3.0).min(3.0) as f64;
        let sustain_level = self.genome.vol_sus.max(0.001) as f64;
        
        let env = envelope(move |t| {
            if t < attack_time {
                (t / attack_time).min(1.0)
            } else if t < attack_time + decay_time {
                let decay_progress = (t - attack_time) / decay_time;
                1.0 - (1.0 - sustain_level) * decay_progress
            } else {
                sustain_level * (-((t - attack_time - decay_time) * 0.1)).exp()
            }
        });
        
        // 应用包络
        let with_envelope = mixed * env;
        
        // 低通滤波器 (最常用的滤波器类型)
        let cutoff_freq = (freq_a * (0.5 + self.genome.flt_freq * 4.0)).clamp(20.0, 20000.0);
        let q_value = (1.0 + self.genome.flt_q * 10.0).clamp(0.5, 10.0);
        
        let filtered = with_envelope >> lowpass_hz(cutoff_freq, q_value);
        
        // 立体声输出
        let stereo = filtered >> split::<U2>();
        
        // 音量调整
        let volume = 0.2;
        let mut graph = stereo * volume;
        
        // 渲染波形
        Wave::render(sample_rate, duration, &mut graph)
    }
}
