use fundsp::hacker::*;

/// 使用固定种子的噪声生成器
/// 输出：白噪声样本
#[derive(Clone)]
pub struct SeededNoise {
    state: u64,
}

impl SeededNoise {
    pub fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    // LCG (Linear Congruential Generator) - 简单但可重现
    fn next_random(&mut self) -> f32 {
        // 使用POSIX LCG参数
        self.state = self.state.wrapping_mul(1103515245).wrapping_add(12345);
        // 转换到 [-1.0, 1.0] 范围
        let value = (self.state >> 16) & 0x7FFF;
        (value as f32 / 16384.0) - 1.0
    }
}

impl AudioNode for SeededNoise {
    const ID: u64 = 92;
    type Inputs = U0;
    type Outputs = U1;

    fn tick(&mut self, _input: &Frame<f32, Self::Inputs>) -> Frame<f32, Self::Outputs> {
        [self.next_random()].into()
    }

    fn set_sample_rate(&mut self, _sample_rate: f64) {
        // 噪声生成不依赖采样率
    }
}
