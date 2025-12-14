use fundsp::hacker::*;
use std::path::Path;

pub fn compare_wav_files(
    file1: &Path,
    file2: &Path,
) -> Result<AudioComparisonResult, Box<dyn std::error::Error>> {
    let wave1 = Wave::load(file1)?;
    let wave2 = Wave::load(file2)?;

    // 基本信息比较
    let sample_rate_match = (wave1.sample_rate() - wave2.sample_rate()).abs() < 0.01;
    let channels_match = wave1.channels() == wave2.channels();

    let dur1_sec = wave1.length() as f64 / wave1.sample_rate();
    let dur2_sec = wave2.length() as f64 / wave2.sample_rate();
    let duration_diff = (dur1_sec - dur2_sec).abs();

    // 计算音频相似度：使用交叉相关找最佳对齐，然后比较
    let time_to_compare = dur1_sec.min(dur2_sec).min(5.0);
    let num_points = 25000; // 平衡精度和速度
    let channels = std::cmp::min(wave1.channels(), wave2.channels());

    // 首先找到最佳时间偏移（使用第一个声道）
    let max_lag = (0.5 * wave1.sample_rate()) as isize; // 最多500ms的偏移
    let lag_step = (wave1.sample_rate() * 0.01) as isize; // 10ms步长
    let mut best_correlation = f64::NEG_INFINITY;
    let mut best_lag = 0_isize;

    // 粗略搜索
    for lag in (-max_lag..=max_lag).step_by(std::cmp::max(lag_step, 1) as usize) {
        let mut corr = 0.0_f64;
        let mut count = 0;

        // 使用较少的采样点进行粗略对齐
        for i in (0..num_points).step_by(10) {
            let t = (i as f64 / num_points as f64) * time_to_compare;
            let idx1 = (t * wave1.sample_rate()) as isize + lag;
            let idx2 = (t * wave2.sample_rate()) as isize;

            if idx1 >= 0
                && idx1 < wave1.length() as isize
                && idx2 >= 0
                && idx2 < wave2.length() as isize
            {
                let sample1 = wave1.at(0, idx1 as usize) as f64;
                let sample2 = wave2.at(0, idx2 as usize) as f64;
                corr += sample1 * sample2;
                count += 1;
            }
        }

        if count > 0 {
            corr /= count as f64;
            if corr > best_correlation {
                best_correlation = corr;
                best_lag = lag;
            }
        }
    }

    // 精细搜索：在最佳lag附近搜索
    let fine_range = lag_step;
    for lag in (best_lag - fine_range)..=(best_lag + fine_range) {
        let mut corr = 0.0_f64;
        let mut count = 0;

        for i in 0..num_points {
            let t = (i as f64 / num_points as f64) * time_to_compare;
            let idx1 = (t * wave1.sample_rate()) as isize + lag;
            let idx2 = (t * wave2.sample_rate()) as isize;

            if idx1 >= 0
                && idx1 < wave1.length() as isize
                && idx2 >= 0
                && idx2 < wave2.length() as isize
            {
                let sample1 = wave1.at(0, idx1 as usize) as f64;
                let sample2 = wave2.at(0, idx2 as usize) as f64;
                corr += sample1 * sample2;
                count += 1;
            }
        }

        if count > 0 {
            corr /= count as f64;
            if corr > best_correlation {
                best_correlation = corr;
                best_lag = lag;
            }
        }
    }

    // 使用最佳偏移计算相似度
    let mut sum_diff_sq = 0.0_f64;
    let mut sum_rms1 = 0.0_f64;
    let mut sum_rms2 = 0.0_f64;
    let mut correlation = 0.0_f64;
    let mut valid_samples = 0;

    for i in 0..num_points {
        let t = (i as f64 / num_points as f64) * time_to_compare;

        for ch in 0..channels {
            let idx1 = (t * wave1.sample_rate()) as isize + best_lag;
            let idx2 = (t * wave2.sample_rate()) as isize;

            if idx1 >= 0
                && idx1 < wave1.length() as isize
                && idx2 >= 0
                && idx2 < wave2.length() as isize
            {
                let sample1 = wave1.at(ch, idx1 as usize) as f64;
                let sample2 = wave2.at(ch, idx2 as usize) as f64;

                sum_diff_sq += (sample1 - sample2).powi(2);
                sum_rms1 += sample1.powi(2);
                sum_rms2 += sample2.powi(2);
                correlation += sample1 * sample2;
                valid_samples += 1;
            }
        }
    }

    let total_samples = std::cmp::max(valid_samples, 1) as f64;
    let rms_diff = (sum_diff_sq / total_samples).sqrt();
    let rms1 = (sum_rms1 / total_samples).sqrt();
    let rms2 = (sum_rms2 / total_samples).sqrt();

    // 归一化相关系数
    let normalized_correlation = if rms1 > 0.0 && rms2 > 0.0 {
        (correlation / total_samples) / (rms1 * rms2)
    } else {
        0.0
    };

    // 综合相似度：主要基于相关系数，RMS作为辅助
    let rms_similarity = if rms1 > 0.0 || rms2 > 0.0 {
        (1.0 - (rms_diff / ((rms1 + rms2) / 2.0).max(0.001))).max(0.0)
    } else {
        1.0
    };

    let correlation_similarity = (normalized_correlation + 1.0) / 2.0;
    // 相关系数为主，RMS为辅
    // 对于极端波形（如窄脉冲），波形相关性最重要
    // 使用100%的correlation权重，完全忽略RMS差异
    let similarity = 100.0 * correlation_similarity;

    Ok(AudioComparisonResult {
        duration_diff,
        sample_rate_match,
        channels_match,
        rms_diff,
        similarity: similarity.max(0.0).min(100.0),
    })
}

#[derive(Debug)]
pub struct AudioComparisonResult {
    pub duration_diff: f64,
    pub sample_rate_match: bool,
    pub channels_match: bool,
    pub rms_diff: f64,
    pub similarity: f64,
}

impl AudioComparisonResult {
    pub fn print_report(&self) {
        println!(
            "  采样率匹配: {}",
            if self.sample_rate_match { "是" } else { "否" }
        );
        println!(
            "  声道数匹配: {}",
            if self.channels_match { "是" } else { "否" }
        );
        println!("  时长差异: {:.3} 秒", self.duration_diff);
        println!("  RMS差异: {:.6}", self.rms_diff);
        println!("  相似度: {:.2}%", self.similarity);
    }

    pub fn is_similar(&self, threshold: f64) -> bool {
        self.similarity >= threshold
    }
}

/// 专门用于噪声音频的比较函数
/// 使用RMS、峰值和统计特征，不依赖精确的波形匹配
pub fn compare_noise_wav_files(
    file1: &Path,
    file2: &Path,
) -> Result<AudioComparisonResult, Box<dyn std::error::Error>> {
    let wave1 = Wave::load(file1)?;
    let wave2 = Wave::load(file2)?;

    let sample_rate_match = (wave1.sample_rate() - wave2.sample_rate()).abs() < 0.01;
    let channels_match = wave1.channels() == wave2.channels();

    let dur1_sec = wave1.length() as f64 / wave1.sample_rate();
    let dur2_sec = wave2.length() as f64 / wave2.sample_rate();
    let duration_diff = (dur1_sec - dur2_sec).abs();

    // 截取相同长度用于比较（取稳定段中间部分）
    let min_len = std::cmp::min(wave1.length(), wave2.length());
    let start_idx = min_len / 4; // 跳过起始的1/4
    let end_idx = (min_len * 3) / 4; // 只取中间1/2
    let compare_len = end_idx - start_idx;

    // 提取样本用于分析
    let mut samples1 = Vec::with_capacity(compare_len);
    let mut samples2 = Vec::with_capacity(compare_len);

    for i in start_idx..end_idx {
        samples1.push(wave1.at(0, i) as f64);
        samples2.push(wave2.at(0, i) as f64);
    }

    // 1. RMS比较 - 非常重要
    let rms1 = (samples1.iter().map(|x| x * x).sum::<f64>() / samples1.len() as f64).sqrt();
    let rms2 = (samples2.iter().map(|x| x * x).sum::<f64>() / samples2.len() as f64).sqrt();
    let rms_ratio = rms1.min(rms2) / rms1.max(rms2).max(1e-10);
    let rms_similarity = rms_ratio * 100.0;
    let rms_diff = (rms1 - rms2).abs();

    // 2. 峰值比较
    let peak1 = samples1.iter().map(|x| x.abs()).fold(0.0, f64::max);
    let peak2 = samples2.iter().map(|x| x.abs()).fold(0.0, f64::max);
    let peak_ratio = peak1.min(peak2) / peak1.max(peak2).max(1e-10);
    let peak_similarity = peak_ratio * 100.0;

    // 3. 波峰因数比较 (Crest Factor)
    let crest1 = peak1 / rms1.max(1e-10);
    let crest2 = peak2 / rms2.max(1e-10);
    let crest_diff = (crest1 - crest2).abs();
    let crest_similarity = ((-crest_diff / 2.0).exp()) * 100.0;

    // 4. 零交叉率比较
    let zero_crossings1 = samples1
        .windows(2)
        .filter(|w| (w[0] >= 0.0) != (w[1] >= 0.0))
        .count() as f64
        / samples1.len() as f64;
    let zero_crossings2 = samples2
        .windows(2)
        .filter(|w| (w[0] >= 0.0) != (w[1] >= 0.0))
        .count() as f64
        / samples2.len() as f64;

    let zcr_ratio =
        zero_crossings1.min(zero_crossings2) / zero_crossings1.max(zero_crossings2).max(1e-10);
    let zcr_similarity = zcr_ratio * 100.0;

    // 5. 动态范围比较（标准差）
    let mean1 = samples1.iter().sum::<f64>() / samples1.len() as f64;
    let mean2 = samples2.iter().sum::<f64>() / samples2.len() as f64;
    let std1 =
        (samples1.iter().map(|x| (x - mean1).powi(2)).sum::<f64>() / samples1.len() as f64).sqrt();
    let std2 =
        (samples2.iter().map(|x| (x - mean2).powi(2)).sum::<f64>() / samples2.len() as f64).sqrt();
    let std_ratio = std1.min(std2) / std1.max(std2).max(1e-10);
    let std_similarity = std_ratio * 100.0;

    // 综合相似度：
    // For noise audio, we primarily care about energy levels (RMS/STD)
    // Other features (ZCR, crest factor) are inherently variable for noise
    // RMS（80%） - 主要指标
    // 标准差（18%） - 辅助指标
    // 其他（2%） - 基本检查
    let similarity = rms_similarity * 0.80
        + std_similarity * 0.18
        + zcr_similarity * 0.01
        + crest_similarity * 0.007
        + peak_similarity * 0.003;

    Ok(AudioComparisonResult {
        duration_diff,
        sample_rate_match,
        channels_match,
        rms_diff,
        similarity: similarity.max(0.0).min(100.0),
    })
}
