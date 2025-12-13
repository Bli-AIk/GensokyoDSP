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
    /// TODO: 需要根据实际测试来精确校准映射关系
    /// 当前观察: a_freq=0.5 -> 524Hz (约C5, MIDI 72)
    fn calculate_frequency(&self, freq_param: f32) -> f32 {
        // 0.5 对应 C5 (524Hz, MIDI 72)
        let midi_note = 72.0 + (freq_param - 0.5) * 48.0;
        440.0 * 2_f32.powf((midi_note - 69.0) / 12.0)
    }
    
    /// 生成波形
    /// TODO (doc line 28-29): 实现锯齿波、方波、脉冲波的变形
    /// 目前只实现了正弦波 (a_form = 0.0)
    fn create_oscillator(&self, freq: f32, form: f32) -> An<impl AudioNode<Inputs = U0, Outputs = U1>> {
        if form < 0.57 {
            // TODO: 正弦波到锯齿波的变形
            sine_hz(freq)
        } else if form < 0.81 {
            // TODO (doc line 28): 锯齿波到方波的变形
            sine_hz(freq)
        } else {
            // TODO (doc line 28): 方波到脉冲波的变形
            sine_hz(freq)
        }
    }
    
    pub fn synthesize_with_params(&self, duration: f64, sample_rate: f64) -> Wave {
        let freq_a = self.calculate_frequency(self.genome.a_freq);
        
        // TODO (doc line 41): 实现振荡器B的频率参数 (b_freq为相对频率)
        let _freq_b = self.calculate_frequency(self.genome.b_freq);
        
        // 创建振荡器A (default中只使用A，因为osc_mix=0.0)
        let osc_a = self.create_oscillator(freq_a, self.genome.a_form);
        
        // TODO (doc line 29): 实现噪声混合 (a_noise, b_noise)
        // TODO (doc line 31): 实现音高调制 (a_mod, b_mod)
        // TODO (doc line 32): 实现噪声特性 (a_color)
        // TODO (doc line 37-42): 实现振荡器B及其所有参数
        // TODO (doc line 34-36): 实现FM调制 (fm_mod, fm_amt, mix_mod)
        // TODO (doc line 36): 实现振荡器混合 (osc_mix)
        // TODO (doc line 40): 实现子振荡器 (sub_am)
        
        // 音量包络 (ADSR)
        // TODO (doc line 46-49): 实现完整包络时间控制 (env_time, env_loop, env_tilt, env_kf)
        // TODO (doc line 52): 实现衰减阶段 (vol_dcy)
        
        // 根据文档51行: vol_atk塑造起音阶段
        // 0.5 = 线性, < 0.5 = 较慢建立, > 0.5 = 较快建立
        let vol_atk = self.genome.vol_atk as f64;
        let attack_time = 0.01; // 固定attack时间，形状由vol_atk控制
        
        let sustain_level = self.genome.vol_sus as f64;
        
        // TODO (doc line 53): 实现音量淡出 (vol_fade > 0.75时激活)
        
        let volume_env = envelope(move |t| {
            if t < attack_time {
                let progress = t / attack_time;
                // 根据vol_atk调整曲线形状
                // < 0.5: 指数上升（较慢）, > 0.5: 更快上升
                if vol_atk < 0.5 {
                    // 慢上升：使用幂函数
                    let curve = 2.0 - vol_atk * 4.0; // 0.0->2.0, 0.5->0.0
                    progress.powf(curve.max(1.0))
                } else {
                    // 快上升：使用根函数
                    let curve = (vol_atk - 0.5) * 4.0 + 1.0; // 0.5->1.0, 1.0->3.0
                    progress.powf(1.0 / curve)
                }
            } else {
                sustain_level
            }
        });
        
        // TODO (doc line 54-57): 实现调制包络 (mod_atk, mod_dcy, mod_sh, mod_vel)
        // TODO (doc line 58-61): 实现LFO (lfo_rate, lfo_amt, lfo_bal, lfo_dly)
        
        // 应用包络
        let with_envelope = osc_a * volume_env;
        
        // 滤波器
        // TODO (doc line 65-70): 实现多种滤波器类型 (flt_type)
        // TODO (doc line 66): 实现Q值/共振 (flt_q)
        // TODO (doc line 67): 实现截止频率调制 (flt_mod)
        // TODO (doc line 68): 实现滤波器分离 (flt_sep)
        // TODO (doc line 70): 实现键盘跟随 (flt_kf)
        // default中 flt_freq=1.0, flt_kf=0.0 表示全开滤波器，无键盘跟随
        let cutoff = (freq_a * (0.5 + self.genome.flt_freq * 15.0)).clamp(20.0, 20000.0);
        let filtered = with_envelope >> lowpass_hz(cutoff, 1.0);
        
        // TODO (doc line 71): 实现饱和度 (saturate)
        // TODO (doc line 72-77): 实现混响和合唱效果 (rvb_mix, rvb_atk, rvb_len, rvb_damp, rvb_chor, rvb_size)
        // TODO (doc line 78-81): 实现EQ调整 (adj_bass, adj_treb, adj_pan, adj_clip)
        
        // 立体声输出
        let stereo = filtered >> split::<U2>();
        
        // 音量调整 - 参考音频RMS约为0.055
        let volume = 0.08;
        let mut graph = stereo * volume;
        
        Wave::render(sample_rate, duration, &mut graph)
    }
    
    pub fn synthesize(&self, duration: f64) -> Wave {
        self.synthesize_with_params(duration, 48000.0)
    }
}
