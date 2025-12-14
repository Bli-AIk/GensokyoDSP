use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SynplantGenome {
    // 振荡器 A (Oscillator A)
    pub a_form: f32,  // 波形形状 (Implemented)
    pub a_noise: f32, // 噪声混合量 // TODO: Implement
    pub a_mod: f32,   // 音高调制量 // TODO: Implement
    pub a_color: f32, // 噪声特性 // TODO: Implement
    pub a_freq: f32,  // 音高 (Implemented)

    // 振荡器 B (Oscillator B)
    pub b_form: f32,  // 波形形状 // TODO: Implement
    pub b_noise: f32, // 噪声混合量 // TODO: Implement
    pub b_mod: f32,   // 音高调制量 // TODO: Implement
    pub b_freq: f32,  // 相对音高 // TODO: Implement
    pub b_sh: f32,    // 采样保持率 // TODO: Implement

    // 调制 (Modulation)
    pub fm_mod: f32,  // FM调制包络 // TODO: Implement
    pub fm_amt: f32,  // FM量 // TODO: Implement
    pub mix_mod: f32, // 混合调制 // TODO: Implement
    pub osc_mix: f32, // 振荡器混合 // TODO: Implement
    pub sub_am: f32,  // 子振荡器幅度调制 // TODO: Implement

    // 包络 (Envelope)
    pub env_time: f32, // 总持续时间 // TODO: Implement
    pub env_loop: f32, // 循环时间 // TODO: Implement
    pub env_tilt: f32, // 倾斜度 // TODO: Implement
    pub env_kf: f32,   // 键盘跟随 // TODO: Implement

    // 音量包络 (Volume Envelope)
    pub vol_atk: f32,  // 起音 (Implemented basic curve)
    pub vol_dcy: f32,  // 衰减 // TODO: Implement
    pub vol_sus: f32,  // 延音 (Implemented basic level)
    pub vol_fade: f32, // 淡出 // TODO: Implement

    // 调制包络 (Modulation Envelope)
    pub mod_atk: f32, // 起音 // TODO: Implement
    pub mod_dcy: f32, // 衰减 // TODO: Implement
    pub mod_sh: f32,  // 采样保持 // TODO: Implement
    pub mod_vel: f32, // 力度 // TODO: Implement

    // LFO
    pub lfo_rate: f32, // 频率 // TODO: Implement
    pub lfo_amt: f32,  // 量 // TODO: Implement
    pub lfo_bal: f32,  // 颤音/震音平衡 // TODO: Implement
    pub lfo_dly: f32,  // 延迟 // TODO: Implement

    // 滤波器 (Filter)
    pub flt_type: f32, // 类型 // TODO: Implement types
    pub flt_q: f32,    // Q值/共振 // TODO: Implement resonance
    pub flt_mod: f32,  // 截止频率调制 // TODO: Implement env mod
    pub flt_sep: f32,  // 分离度 // TODO: Implement stereo separation
    pub flt_freq: f32, // 截止频率 (Implemented basic mapping)
    pub flt_kf: f32,   // 键盘跟随 // TODO: Implement

    // 效果 (Effects)
    pub saturate: f32, // 饱和度 // TODO: Implement
    pub rvb_mix: f32,  // 混响混合 // TODO: Implement
    pub rvb_atk: f32,  // 混响包络 // TODO: Implement
    pub rvb_len: f32,  // 混响长度 // TODO: Implement
    pub rvb_damp: f32, // 混响阻尼 // TODO: Implement
    pub rvb_chor: f32, // 合唱量 // TODO: Implement
    pub rvb_size: f32, // 混响大小 // TODO: Implement

    // 调整 (Adjustments)
    pub adj_bass: f32, // 低音 // TODO: Implement EQ
    pub adj_treb: f32, // 高音 // TODO: Implement EQ
    pub adj_pan: f32,  // 声相 // TODO: Implement Panning
    pub adj_clip: f32, // 软剪辑 // TODO: Implement Limiter/Clip
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SynplantPatch {
    pub name: String,
    pub genome: SynplantGenome,
}

impl SynplantPatch {
    pub fn from_ron_file<P: AsRef<std::path::Path>>(
        path: P,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let patch: SynplantPatch = ron::from_str(&content)?;
        Ok(patch)
    }

    pub fn from_ron_str(content: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let patch: SynplantPatch = ron::from_str(content)?;
        Ok(patch)
    }
}
