use fundsp::hacker::*;
use std::f64::consts::PI;

/// 自定义波形变形振荡器
/// Inputs: Frequency (Hz), Form (0.0 - 1.0)
/// Output: Waveform Sample
#[derive(Clone)]
pub struct MorphOscillator {
    phase: f64,
    sample_rate: f64,
}

impl MorphOscillator {
    pub fn new(sample_rate: f64) -> Self {
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

            let _k = 1.0 - even_odd_ratio; // Added underscore to suppress warning

            let rolloff_strength = if form >= 0.64 && form <= 0.71 {
                35.0
            } else if form >= 0.6 && form <= 0.77 {
                28.0
            } else {
                20.0
            };

            let saw_p = Self::generate_saw(p, rolloff_strength);
            let saw_shifted = Self::generate_saw(p - 0.5, rolloff_strength);

            // Phase 2: Saw (O+E) -> Square (O)
            // Target = Odd + ratio * Even
            // Odd = 0.5 * (S - S')
            // Even = 0.5 * (S + S')
            // Target = 0.5 * [ (1+ratio)S - (1-ratio)S' ]

            0.5 * ((1.0 + even_odd_ratio) * saw_p - (1.0 - even_odd_ratio) * saw_shifted)
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

            let rolloff_strength = if duty_cycle > 0.97 {
                15.0
            } else if duty_cycle > 0.94 {
                25.0
            } else if duty_cycle > 0.93 {
                30.0
            } else if duty_cycle > 0.9 {
                35.0
            } else {
                20.0
            };

            // Phase 3: Square (O) -> Pulse
            // Must match Phase 2 end: 0.5 * (S(p) - S(p-0.5))
            // Formula: 0.5 * (Saw(p - 0.5 - d) - Saw(p - 0.5))
            // When d=0.5: 0.5 * (S(p-1) - S(p-0.5)) = 0.5 * (S(p) - S(p-0.5)) -> Matches Square
            // When d=1.0: 0.5 * (S(p-1.5) - S(p-0.5)) = 0 -> Matches Pulse width 0

            // We need custom generate_saw to support variable max_harmonics if needed,
            // but for now generate_saw (64 harmonics) is consistent with Phase 2.
            // However, Phase 3 needs more harmonics for sharpness.

            let max_harmonics = if duty_cycle > 0.97 {
                512
            } else if duty_cycle > 0.94 {
                384
            } else if duty_cycle > 0.93 {
                256
            } else if duty_cycle > 0.9 {
                128
            } else {
                64
            };

            let saw_base = Self::generate_saw_custom(p - 0.5, max_harmonics, rolloff_strength);
            let saw_mod =
                Self::generate_saw_custom(p - 0.5 - duty_cycle, max_harmonics, rolloff_strength);

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
