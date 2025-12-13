use fundsp::hacker::*;
use std::path::Path;

pub fn compare_wav_files(file1: &Path, file2: &Path) -> Result<AudioComparisonResult, Box<dyn std::error::Error>> {
    let wave1 = Wave::load(file1)?;
    let wave2 = Wave::load(file2)?;
    
    // 基本信息比较
    let sample_rate_match = (wave1.sample_rate() - wave2.sample_rate()).abs() < 0.01;
    let channels_match = wave1.channels() == wave2.channels();
    
    let dur1_sec = wave1.length() as f64 / wave1.sample_rate();
    let dur2_sec = wave2.length() as f64 / wave2.sample_rate();
    let duration_diff = (dur1_sec - dur2_sec).abs();
    
    // 计算音频相似度：采样重采样后比较
    let time_to_compare = dur1_sec.min(dur2_sec).min(5.0);
    let num_points = 5000;
    let channels = std::cmp::min(wave1.channels(), wave2.channels());
    
    let mut sum_diff_sq = 0.0_f64;
    let mut sum_rms1 = 0.0_f64;
    let mut sum_rms2 = 0.0_f64;
    let mut correlation = 0.0_f64;
    
    for i in 0..num_points {
        let t = (i as f64 / num_points as f64) * time_to_compare;
        
        for ch in 0..channels {
            let idx1 = std::cmp::min((t * wave1.sample_rate()) as usize, wave1.length() - 1);
            let idx2 = std::cmp::min((t * wave2.sample_rate()) as usize, wave2.length() - 1);
            
            let sample1 = wave1.at(ch, idx1) as f64;
            let sample2 = wave2.at(ch, idx2) as f64;
            
            sum_diff_sq += (sample1 - sample2).powi(2);
            sum_rms1 += sample1.powi(2);
            sum_rms2 += sample2.powi(2);
            correlation += sample1 * sample2;
        }
    }
    
    let total_samples = (num_points * channels) as f64;
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
    // 增加相关系数的权重，因为它更能反映波形形状的相似性
    let similarity = 100.0 * (rms_similarity * 0.2 + correlation_similarity * 0.8);
    
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
    
    pub fn is_similar(&self, threshold: f64) -> bool {
        self.similarity >= threshold
    }
}
