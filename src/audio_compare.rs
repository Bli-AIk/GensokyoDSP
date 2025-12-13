use fundsp::hacker::*;
use std::path::Path;

pub fn compare_wav_files(file1: &Path, file2: &Path) -> Result<AudioComparisonResult, Box<dyn std::error::Error>> {
    let wave1 = Wave::load(file1)?;
    let wave2 = Wave::load(file2)?;
    
    // 基本信息比较
    let duration_diff = (wave1.length() as f64 - wave2.length() as f64).abs();
    let sample_rate_match = (wave1.sample_rate() - wave2.sample_rate()).abs() < 0.01;
    let channels_match = wave1.channels() == wave2.channels();
    
    // 计算音频相似度 (简化版：比较前1000个样本的RMS差异)
    let samples_to_compare = std::cmp::min(1000, std::cmp::min(wave1.length(), wave2.length()));
    let mut sum_diff_sq = 0.0_f64;
    let mut sum_rms1 = 0.0_f64;
    let mut sum_rms2 = 0.0_f64;
    
    for i in 0..samples_to_compare {
        for ch in 0..std::cmp::min(wave1.channels(), wave2.channels()) {
            let sample1 = wave1.at(ch, i) as f64;
            let sample2 = wave2.at(ch, i) as f64;
            sum_diff_sq += (sample1 - sample2).powi(2);
            sum_rms1 += sample1.powi(2);
            sum_rms2 += sample2.powi(2);
        }
    }
    
    let rms_diff = (sum_diff_sq / samples_to_compare as f64).sqrt();
    let rms1 = (sum_rms1 / samples_to_compare as f64).sqrt();
    let rms2 = (sum_rms2 / samples_to_compare as f64).sqrt();
    
    // 相似度百分比 (基于RMS差异)
    let similarity = if rms1 > 0.0 || rms2 > 0.0 {
        100.0 * (1.0 - (rms_diff / ((rms1 + rms2) / 2.0).max(0.001)))
    } else {
        100.0
    };
    
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
        println!("  采样率匹配: {}", if self.sample_rate_match { "是" } else { "否" });
        println!("  声道数匹配: {}", if self.channels_match { "是" } else { "否" });
        println!("  时长差异: {:.3} 秒", self.duration_diff);
        println!("  RMS差异: {:.6}", self.rms_diff);
        println!("  相似度: {:.2}%", self.similarity);
    }
}
