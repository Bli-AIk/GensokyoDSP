use fundsp::hacker::*;

/// Colored noise generator with adjustable spectrum
/// color: 0.0 = brown/red (low freq dominant), 1.0 = white (flat spectrum)
#[derive(Clone)]
pub struct ColoredNoise {
    state: u64,
    // Paul Kellet的粉红噪声滤波器状态 (7个累加器)
    b0: f32,
    b1: f32,
    b2: f32,
    b3: f32,
    b4: f32,
    b5: f32,
    b6: f32,
    // 棕色噪声累加器
    brown: f32,
    color: f32,
}

impl ColoredNoise {
    pub fn new(seed: u64, color: f32) -> Self {
        Self {
            state: seed,
            b0: 0.0,
            b1: 0.0,
            b2: 0.0,
            b3: 0.0,
            b4: 0.0,
            b5: 0.0,
            b6: 0.0,
            brown: 0.0,
            color: color.clamp(0.0, 1.0),
        }
    }

    fn next_white(&mut self) -> f32 {
        // LCG生成白噪声
        self.state = self.state.wrapping_mul(1103515245).wrapping_add(12345);
        let value = (self.state >> 16) & 0x7FFF;
        (value as f32 / 16384.0) - 1.0
    }

    fn generate_sample(&mut self) -> f32 {
        let white = self.next_white();

        // Paul Kellet的粉红噪声算法
        // 使用7个加权的一阶低通滤波器
        self.b0 = 0.99886 * self.b0 + white * 0.0555179;
        self.b1 = 0.99332 * self.b1 + white * 0.0750759;
        self.b2 = 0.96900 * self.b2 + white * 0.1538520;
        self.b3 = 0.86650 * self.b3 + white * 0.3104856;
        self.b4 = 0.55000 * self.b4 + white * 0.5329522;
        self.b5 = -0.7616 * self.b5 - white * 0.0168980;
        let pink =
            self.b0 + self.b1 + self.b2 + self.b3 + self.b4 + self.b5 + self.b6 + white * 0.5362;
        self.b6 = white * 0.115926;

        // 棕色噪声：积分白噪声
        self.brown = (self.brown + white * 0.02).clamp(-1.0, 1.0);
        let brown = self.brown;

        // 在棕色、粉红和白噪声之间混合
        // color=0.0 -> brown, color=0.5 -> pink, color=1.0 -> white
        let mixed = if self.color < 0.5 {
            // 0.0-0.5: 从棕色过渡到粉红
            let t = self.color * 2.0;
            brown * (1.0 - t) + pink * t
        } else {
            // 0.5-1.0: 从粉红过渡到白色
            let t = (self.color - 0.5) * 2.0;
            pink * (1.0 - t) + white * t
        };

        // 增益补偿以保持RMS稳定
        // 最新测量数据（第四轮）：
        // color=0.0-0.15: 1.03-1.19倍 - 很好
        // color=0.25-0.45: 1.29-1.42倍 - 稍高，可接受
        // color=0.55: 0.97倍 - 完美！
        // color=0.6-1.0: 0.37-0.72倍 - 需要提高2-3倍

        let gain = if self.color < 0.2 {
            // 低color：保持不变
            0.57 + self.color * 0.25 // 0.57 -> 0.62
        } else if self.color < 0.4 {
            // 低到中color：略微降低
            0.62 - (self.color - 0.2) * 1.1 // 0.62 -> 0.40
        } else if self.color < 0.52 {
            // 中color：降低到最小（调整拐点从0.55到0.52）
            0.40 - (self.color - 0.4) * 1.7 // 0.40 -> 0.20
        } else if self.color < 0.7 {
            // 中高color：快速增加（0.5506需要约0.27）
            0.20 + (self.color - 0.52) * 1.6 // 0.20 -> 0.49
        } else {
            // 高color：继续增加
            0.49 + (self.color - 0.7) * 1.4 // 0.49 -> 0.91
        };

        mixed * gain
    }
}

impl AudioNode for ColoredNoise {
    const ID: u64 = 93;
    type Inputs = U0;
    type Outputs = U1;

    fn tick(&mut self, _input: &Frame<f32, Self::Inputs>) -> Frame<f32, Self::Outputs> {
        [self.generate_sample()].into()
    }

    fn set_sample_rate(&mut self, _sample_rate: f64) {
        // 噪声生成不依赖采样率（或者可以根据采样率调整滤波器系数）
    }

    fn reset(&mut self) {
        // 重置滤波器状态
        self.b0 = 0.0;
        self.b1 = 0.0;
        self.b2 = 0.0;
        self.b3 = 0.0;
        self.b4 = 0.0;
        self.b5 = 0.0;
        self.b6 = 0.0;
        self.brown = 0.0;
    }
}
