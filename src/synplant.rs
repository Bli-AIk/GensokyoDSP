use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SynplantGenome {
    // 振荡器 A (Oscillator A)
    pub a_form: f32,        // 波形形状
    pub a_noise: f32,       // 噪声混合量
    pub a_mod: f32,         // 音高调制量
    pub a_color: f32,       // 噪声特性
    pub a_freq: f32,        // 音高
    
    // 振荡器 B (Oscillator B)
    pub b_form: f32,        // 波形形状
    pub b_noise: f32,       // 噪声混合量
    pub b_mod: f32,         // 音高调制量
    pub b_freq: f32,        // 相对音高
    pub b_sh: f32,          // 采样保持率
    
    // 调制 (Modulation)
    pub fm_mod: f32,        // FM调制包络
    pub fm_amt: f32,        // FM量
    pub mix_mod: f32,       // 混合调制
    pub osc_mix: f32,       // 振荡器混合
    pub sub_am: f32,        // 子振荡器幅度调制
    
    // 包络 (Envelope)
    pub env_time: f32,      // 总持续时间
    pub env_loop: f32,      // 循环时间
    pub env_tilt: f32,      // 倾斜度
    pub env_kf: f32,        // 键盘跟随
    
    // 音量包络 (Volume Envelope)
    pub vol_atk: f32,       // 起音
    pub vol_dcy: f32,       // 衰减
    pub vol_sus: f32,       // 延音
    pub vol_fade: f32,      // 淡出
    
    // 调制包络 (Modulation Envelope)
    pub mod_atk: f32,       // 起音
    pub mod_dcy: f32,       // 衰减
    pub mod_sh: f32,        // 采样保持
    pub mod_vel: f32,       // 力度
    
    // LFO
    pub lfo_rate: f32,      // 频率
    pub lfo_amt: f32,       // 量
    pub lfo_bal: f32,       // 颤音/震音平衡
    pub lfo_dly: f32,       // 延迟
    
    // 滤波器 (Filter)
    pub flt_type: f32,      // 类型
    pub flt_q: f32,         // Q值/共振
    pub flt_mod: f32,       // 截止频率调制
    pub flt_sep: f32,       // 分离度
    pub flt_freq: f32,      // 截止频率
    pub flt_kf: f32,        // 键盘跟随
    
    // 效果 (Effects)
    pub saturate: f32,      // 饱和度
    pub rvb_mix: f32,       // 混响混合
    pub rvb_atk: f32,       // 混响包络
    pub rvb_len: f32,       // 混响长度
    pub rvb_damp: f32,      // 混响阻尼
    pub rvb_chor: f32,      // 合唱量
    pub rvb_size: f32,      // 混响大小
    
    // 调整 (Adjustments)
    pub adj_bass: f32,      // 低音
    pub adj_treb: f32,      // 高音
    pub adj_pan: f32,       // 声相
    pub adj_clip: f32,      // 软剪辑
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SynplantPatch {
    pub name: String,
    pub genome: SynplantGenome,
}

impl SynplantPatch {
    pub fn from_ron_file(path: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let patch: SynplantPatch = ron::from_str(&content)?;
        Ok(patch)
    }
}
