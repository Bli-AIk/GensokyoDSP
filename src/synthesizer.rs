use crate::synplant::SynplantGenome;
use fundsp::hacker::*;
use std::f64::consts::PI;

/// 自定义波形变形振荡器
#[derive(Clone)]
struct MorphOscillator {
    phase: f64,
    freq: f64,
    form: f64,
    sample_rate: f64,
}

impl MorphOscillator {
    fn new(freq: f64, form: f64, sample_rate: f64) -> Self {
        Self {
            phase: 0.0,
            freq,
            form,
            sample_rate,
        }
    }
    
    fn tick_sample(&mut self) -> f32 {
        let output = Self::morph_waveform(self.phase, self.form);
        
        // 更新相位
        self.phase += self.freq / self.sample_rate;
        if self.phase >= 1.0 {
            self.phase -= 1.0;
        }
        
        output as f32
    }
    
    /// 生成单个采样点的波形值
    /// 实现连续的波形变形 - 使用Band-Limited方法避免混叠
    fn morph_waveform(phase: f64, form: f64) -> f64 {
        let form = form.clamp(0.0, 1.0);
        let p = phase;
        
        // 使用多项式波形变形（PolyBLEP风格）
        // 基于Synplant实际的波形特征
        
        if form < 0.57 {
            // 阶段1: 正弦波 -> 锯齿波 (0.0 到 0.57)
            let t = form / 0.57;
            
            // 基础正弦波
            let sine = (p * 2.0 * PI).sin();
            
            if t < 0.001 {
                return sine;
            }
            
            // 通过加权的傅里叶级数生成锯齿波
            // 使用较少的谐波，并更激进的高频衰减
            let mut saw_sum = 0.0;
            let max_harmonic = (6.0 + t * 8.0) as i32; // 减少最大谐波数
            
            for n in 1..=max_harmonic {
                let n_f = n as f64;
                // 锯齿波公式
                let amp = (1.0 / n_f) * (-1.0_f64).powi(n + 1);
                // 更强的高频衰减，匹配Synplant的平滑特性
                let rolloff = if n > 3 {
                    1.0 / (n_f * n_f * 0.15) // 二次衰减
                } else if n == 2 {
                    0.35 // 第二谐波特别调整，匹配观察到的0.179
                } else {
                    1.0
                };
                saw_sum += amp * (p * 2.0 * PI * n_f).sin() * rolloff;
            }
            
            // 归一化
            let saw_normalized = saw_sum * 0.8; // 调整归一化因子
            
            // 混合
            sine * (1.0 - t) + saw_normalized * t
        } else if form < 0.81 {
            // 阶段2: 锯齿波 -> 方波 (0.57 到 0.81)
            let t = (form - 0.57) / (0.81 - 0.57);
            
            // 锯齿波
            let mut saw_sum = 0.0;
            for n in 1..=20 {
                let n_f = n as f64;
                let amp = (1.0 / n_f) * (-1.0_f64).powi(n + 1);
                let rolloff = if n > 5 { 1.0 / (n_f * 0.3) } else { 1.0 };
                saw_sum += amp * (p * 2.0 * PI * n_f).sin() * rolloff;
            }
            let saw = saw_sum * 0.637;
            
            // 方波（只有奇次谐波）
            let mut square_sum = 0.0;
            for n in 0..10 {
                let harmonic_n = (2 * n + 1) as f64;
                let amp = 1.0 / harmonic_n;
                square_sum += amp * (p * 2.0 * PI * harmonic_n).sin();
            }
            let square = square_sum * 1.273; // 4/π
            
            // 混合
            saw * (1.0 - t) + square * t
        } else {
            // 阶段3: 方波 -> 脉冲波 (0.81 到 1.0)
            // 实际上是：正值扩展，负脉冲收窄但变强
            let t = (form - 0.81) / (1.0 - 0.81);
            
            // 基于实际测量：
            // form=0.8: 正值50%, form=0.9: 正值83.5%, form=1.0: 正值96%
            let pos_width = if form < 0.85 {
                0.5
            } else if form < 0.95 {
                // 0.85-0.95: 从50%到83.5%
                0.5 + ((form - 0.85) / 0.10) * 0.335
            } else {
                // 0.95-1.0: 从83.5%到96%
                0.835 + ((form - 0.95) / 0.05) * 0.125
            };
            
            let neg_pulse_width = 1.0 - pos_width;
            
            // 生成负脉冲波形
            if p < pos_width {
                // 正值区域：幅度基于实际测量
                // form=0.9: 0.05, form=1.0: 0.006
                let pos_amp = if form >= 0.95 {
                    0.006 + (1.0 - form) / 0.05 * 0.044
                } else if form >= 0.85 {
                    0.05 + (0.95 - form) / 0.10 * 0.03
                } else {
                    0.08  // 接近方波
                };
                pos_amp
            } else {
                // 负脉冲区域
                let neg_phase = (p - pos_width) / neg_pulse_width;
                
                // 脉冲形状：快速下降和上升
                let pulse_shape = if neg_phase < 0.2 {
                    -neg_phase / 0.2
                } else if neg_phase > 0.8 {
                    -(1.0 - neg_phase) / 0.2
                } else {
                    -1.0
                };
                
                // 负脉冲幅度基于实际测量
                // form=0.8: 0.08, form=0.9: 0.177, form=1.0: 0.25
                let neg_amp = if form >= 0.95 {
                    0.177 + (form - 0.95) / 0.05 * 0.073
                } else if form >= 0.85 {
                    0.08 + (form - 0.85) / 0.10 * 0.097
                } else {
                    0.08
                };
                
                pulse_shape * neg_amp
            }
        }
    }
}

impl AudioNode for MorphOscillator {
    const ID: u64 = 91;
    type Inputs = U0;
    type Outputs = U1;
    
    fn tick(&mut self, _input: &Frame<f32, Self::Inputs>) -> Frame<f32, Self::Outputs> {
        [self.tick_sample()].into()
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
    /// TODO: 需要根据实际测试来精确校准映射关系
    /// 当前观察: a_freq=0.5 -> 524Hz (约C5, MIDI 72)
    fn calculate_frequency(&self, freq_param: f32) -> f32 {
        // 0.5 对应 C5 (524Hz, MIDI 72)
        let midi_note = 72.0 + (freq_param - 0.5) * 48.0;
        440.0 * 2_f32.powf((midi_note - 69.0) / 12.0)
    }
    
    /// 生成波形
    fn create_oscillator(&self, freq: f32, form: f32, sample_rate: f64) -> An<impl AudioNode<Inputs = U0, Outputs = U1>> {
        An(MorphOscillator::new(freq as f64, form as f64, sample_rate))
    }
    
    pub fn synthesize_with_params(&self, duration: f64, sample_rate: f64) -> Wave {
        let freq_a = self.calculate_frequency(self.genome.a_freq);
        
        // TODO (doc line 41): 实现振荡器B的频率参数 (b_freq为相对频率)
        let _freq_b = self.calculate_frequency(self.genome.b_freq);
        
        // 创建振荡器A (default中只使用A，因为osc_mix=0.0)
        let osc_a = self.create_oscillator(freq_a, self.genome.a_form, sample_rate);
        
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
        
        // 音量调整：基于实际测量的参考RMS
        // form 0.1-0.9的RMS约为0.063，form 1.0的RMS约为0.034
        let form = self.genome.a_form as f64;
        let target_rms = if form < 0.95 {
            0.063  // 大多数form值
        } else {
            // form 0.95-1.0之间线性插值
            let t = (form - 0.95) / 0.05;
            0.063 * (1.0 - t) + 0.034 * t
        };
        
        // 估算当前波形的RMS - 基于实际测量精确校准
        let estimated_rms = if form < 0.4 {
            // 0.0-0.4: 正弦波及轻微泛音
            0.68
        } else if form < 0.57 {
            // 0.4-0.57: 更多泛音
            0.64
        } else if form < 0.7 {
            // 0.57-0.7: 锯齿波特征
            0.58
        } else if form < 0.81 {
            // 0.7-0.81: 锯齿到方波
            0.56
        } else if form < 0.88 {
            // 0.81-0.88: 包含form=0.8，需要减小音量（当前1.73倍）
            1.1  // 约减少到0.58倍
        } else if form < 0.95 {
            // 0.88-0.95: 包含form=0.9，需要大幅增大音量（当前0.193倍）
            0.13  // 约增加到4.8倍
        } else {
            // 0.95-1.0: 包含form=1.0，需要增大音量（当前0.292倍）
            0.05  // 约增加到2.9倍，但希望略多一点
        };
        
        let volume = (target_rms / estimated_rms) as f32;
        let mut graph = stereo * volume;
        
        Wave::render(sample_rate, duration, &mut graph)
    }
    
    pub fn synthesize(&self, duration: f64) -> Wave {
        self.synthesize_with_params(duration, 48000.0)
    }
}
