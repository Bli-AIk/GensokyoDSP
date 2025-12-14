use fundsp::hacker::*;

/// Target RMS values (measured from reference audio)
static TARGET_RMS_TABLE: &[(f64, f64)] = &[
    (0.00, 0.063),
    (0.05, 0.063014),
    (0.10, 0.056808),
    (0.15, 0.063015),
    (0.20, 0.056811),
    (0.25, 0.063021),
    (0.30, 0.056822),
    (0.35, 0.063041),
    (0.40, 0.056850),
    (0.45, 0.063094),
    (0.50, 0.056965),
    (0.55, 0.063219),
    (0.60, 0.058848),
    (0.65, 0.064342),
    (0.70, 0.057971),
    (0.75, 0.065266),
    (0.80, 0.059344),
    (0.85, 0.066154),
    (0.90, 0.061865),
    (0.95, 0.047197),
    (1.00, 0.030622),
];

/// Estimated RMS values (theoretical/calculated)
static ESTIMATED_RMS_TABLE: &[(f64, f64)] = &[
    (0.00, 0.707),
    (0.05, 0.704),
    (0.10, 0.696),
    (0.15, 0.684),
    (0.20, 0.670),
    (0.25, 0.653),
    (0.30, 0.634),
    (0.35, 0.615),
    (0.40, 0.597),
    (0.45, 0.580),
    (0.50, 0.566),
    (0.55, 0.558),
    (0.57, 0.506),
    (0.60, 0.505),
    (0.65, 0.502),
    (0.70, 0.498),
    (0.75, 0.493),
    (0.80, 0.488),
    (0.85, 0.464),
    (0.90, 0.340),
    (0.95, 0.152),
    (1.00, 0.065),
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
pub struct RmsCompensator;

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
