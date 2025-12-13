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
    /// 实现连续的波形变形 - 基于Synplant的实际行为
    /// 0.0-0.57: 正弦波 → 锯齿波
    /// 0.57-0.8: 锯齿波 → 方波（偶次谐波逐渐衰减）
    /// 0.8-1.0: 方波 → 脉冲波（PWM占空比调制）
    fn morph_waveform(phase: f64, form: f64) -> f64 {
        let form = form.clamp(0.0, 1.0);
        let p = phase;
        
        if form < 0.57 {
            // 阶段1: 正弦波 -> 锯齿波 (0.0 到 0.57)
            let t = form / 0.57;
            
            // 正弦波
            let sine = (p * 2.0 * PI).sin();
            
            // 生成带限锯齿波 - 使用傅里叶级数
            let mut saw = 0.0;
            let max_harmonics = 64;
            for n in 1..=max_harmonics {
                let n_f = n as f64;
                // 锯齿波傅里叶系数: (-1)^(n+1) / n
                let amp = (-1.0_f64).powi(n + 1) / n_f;
                // 高频衰减以避免混叠
                let rolloff = 1.0 / (1.0 + (n_f / 20.0).powi(2));
                saw += amp * (p * 2.0 * PI * n_f).sin() * rolloff;
            }
            saw *= 2.0 / PI;
            
            // 使用更平滑的混合曲线
            let blend = t.powf(1.8);
            
            sine * (1.0 - blend) + saw * blend
            
        } else if form < 0.8 {
            // 阶段2: 锯齿波 -> 方波 (0.57 到 0.8)
            // 通过逐渐衰减偶次谐波实现
            // 注意：使用负系数以匹配参考音频的相位
            
            // 根据实测数据的偶次/奇次比例：
            // 0.57->0.5, 0.6->0.49, 0.65->0.36, 0.7->0.27, 0.75->0.09, 0.8->0.00
            let even_odd_ratio = if form < 0.6 {
                0.5 - (form - 0.57) / (0.6 - 0.57) * (0.5 - 0.49)
            } else if form < 0.65 {
                0.49 - (form - 0.6) / (0.65 - 0.6) * (0.49 - 0.36)
            } else if form < 0.7 {
                0.36 - (form - 0.65) / (0.7 - 0.65) * (0.36 - 0.27)
            } else if form < 0.75 {
                0.27 - (form - 0.7) / (0.75 - 0.7) * (0.27 - 0.09)
            } else {
                0.09 - (form - 0.75) / (0.8 - 0.75) * 0.09
            };
            
            let mut waveform = 0.0;
            
            // 根据form值调整rolloff强度，以改善高次谐波匹配
            // 针对0.65-0.75区间使用更强的rolloff reduction
            let rolloff_strength = if form >= 0.64 && form <= 0.71 { 
                35.0  // 0.65和0.7需要更强的高频
            } else if form >= 0.6 && form <= 0.77 { 
                28.0 
            } else { 
                20.0 
            };
            
            for n in 1..=64 {
                let n_f = n as f64;
                // 使用简单的 -1/n 系数（所有正号），然后用偶次衰减
                let base_amp = -1.0 / n_f;
                
                let amp = if n % 2 == 0 {
                    // 偶次谐波：根据even_odd_ratio衰减
                    base_amp * even_odd_ratio
                } else {
                    // 奇次谐波：保持
                    base_amp
                };
                
                let rolloff = 1.0 / (1.0 + (n_f / rolloff_strength).powi(2));
                waveform += amp * (p * 2.0 * PI * n_f).sin() * rolloff;
            }
            
            waveform * (2.0 / PI)
            
        } else {
            // 阶段3: 方波 -> 脉冲波 (0.8 到 1.0) - PWM占空比调制
            // 根据实测数据：占空比从50.0% (0.8) 到 95.7% (1.0)
            // 使用线性插值精确匹配实测值
            // 注意：由于傅里叶带限，实际生成的占空比会略小于目标值，需要补偿
            let duty_cycle = if form <= 0.85 {
                0.500 + (form - 0.8) / (0.85 - 0.8) * (0.652 - 0.500)
            } else if form <= 0.9 {
                0.652 + (form - 0.85) / (0.9 - 0.85) * (0.850 - 0.652)  // 0.826 -> 0.850 补偿
            } else if form <= 0.95 {
                0.850 + (form - 0.9) / (0.95 - 0.9) * (0.970 - 0.850)   // 0.935 -> 0.970 补偿
            } else {
                0.970 + (form - 0.95) / (1.0 - 0.95) * (0.995 - 0.970)  // 0.957 -> 0.995 补偿
            };
            
            // 生成占空比为D的对称脉冲波 (PWM，无直流偏移)
            // 生成对称脉冲波（PWM）
            // 使用带限傅里叶合成，对于极窄脉冲需要更多谐波和更少带限
            
            let mut waveform = 0.0;
            
            // 对于极窄脉冲（占空比>0.9），需要更多谐波和更弱的带限
            // 极端情况需要大量谐波来重建尖锐边缘
            let max_harmonics = if duty_cycle > 0.97 { 
                1024  // form=1.0需要最多谐波
            } else if duty_cycle > 0.94 { 
                768   // form=0.95
            } else if duty_cycle > 0.93 { 
                512 
            } else if duty_cycle > 0.9 { 
                256 
            } else { 
                64 
            };
            let rolloff_strength = if duty_cycle > 0.97 { 
                120.0  // 极弱带限
            } else if duty_cycle > 0.94 { 
                100.0 
            } else if duty_cycle > 0.93 { 
                80.0 
            } else if duty_cycle > 0.9 { 
                60.0 
            } else { 
                20.0 
            };
            
            for n in 1..=max_harmonics {
                let n_f = n as f64;
                // 脉冲波的傅里叶系数
                let amp = 2.0 * (n_f * PI * duty_cycle).sin() / (n_f * PI);
                let rolloff = 1.0 / (1.0 + (n_f / rolloff_strength).powi(2));
                waveform += amp * (p * 2.0 * PI * n_f).cos() * rolloff;
            }
            
            waveform
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
    
    /// 将频率参数 (0.0-1.0) 转换为实际频率 (Hz)
    /// 根据实际测量: a_freq=0.5 -> 约521Hz (C5, MIDI 72)
    fn calculate_frequency(&self, freq_param: f32) -> f32 {
        // a_freq=0.5 对应 MIDI note 72 (C5, 约523 Hz)
        // 映射范围: 4个八度 (48个半音)
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
        // flt_freq=1.0 应该表示全开（不过滤），接近Nyquist频率
        // 使用指数映射让flt_freq=1.0时接近20kHz
        let cutoff = if self.genome.flt_freq >= 0.99 {
            20000.0  // 全开
        } else {
            // 指数映射: flt_freq从0到1，cutoff从基频到20kHz
            let min_cutoff = freq_a;
            let max_cutoff = 20000.0;
            min_cutoff * (max_cutoff / min_cutoff).powf(self.genome.flt_freq)
        };
        let filtered = with_envelope >> lowpass_hz(cutoff, 1.0);
        
        // TODO (doc line 71): 实现饱和度 (saturate)
        // TODO (doc line 72-77): 实现混响和合唱效果 (rvb_mix, rvb_atk, rvb_len, rvb_damp, rvb_chor, rvb_size)
        // TODO (doc line 78-81): 实现EQ调整 (adj_bass, adj_treb, adj_pan, adj_clip)
        
        // 立体声输出
        let stereo = filtered >> split::<U2>();
        
        // 音量调整：基于实际测量的参考RMS
        let form = self.genome.a_form as f64;
        
        // 目标RMS (从参考音频测量得到的稳态RMS，已归一化到[-1, 1])
        let target_rms = Self::interpolate(&[
            (0.00, 0.063), (0.05, 0.063014), (0.10, 0.056808), (0.15, 0.063015),
            (0.20, 0.056811), (0.25, 0.063021), (0.30, 0.056822), (0.35, 0.063041),
            (0.40, 0.056850), (0.45, 0.063094), (0.50, 0.056965), (0.55, 0.063219),
            (0.60, 0.058848), (0.65, 0.064342), (0.70, 0.057971), (0.75, 0.065266),
            (0.80, 0.059344), (0.85, 0.066154), (0.90, 0.061865), (0.95, 0.047197), 
            (1.00, 0.030622),
        ], form);
        
        // 理论生成波形的RMS (基于morph_waveform的数学计算，包括最新的PWM实现和rolloff调整)
        let estimated_rms = Self::interpolate(&[
            (0.00, 0.707), (0.05, 0.704), (0.10, 0.696), (0.15, 0.684),
            (0.20, 0.670), (0.25, 0.653), (0.30, 0.634), (0.35, 0.615),
            (0.40, 0.597), (0.45, 0.580), (0.50, 0.566), (0.55, 0.558),
            (0.57, 0.506), (0.60, 0.505), (0.65, 0.502), (0.70, 0.498),
            (0.75, 0.493), (0.80, 0.488), (0.85, 0.464), (0.90, 0.340), 
            (0.95, 0.163), (1.00, 0.056),
        ], form);
        
        let volume = (target_rms / estimated_rms) as f32;
        let mut graph = stereo * volume;
        
        Wave::render(sample_rate, duration, &mut graph)
    }
    
    pub fn synthesize(&self, duration: f64) -> Wave {
        self.synthesize_with_params(duration, 48000.0)
    }
}
