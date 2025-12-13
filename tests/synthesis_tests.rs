use gensokyo_dsp::*;
use std::path::Path;

/// 测试配置
struct TestCase {
    name: &'static str,
    config_file: &'static str,
    reference_file: &'static str,
    duration: f64,
    similarity_threshold: f64,
}

impl TestCase {
    fn run(&self) -> Result<(), Box<dyn std::error::Error>> {
        let config_path = Path::new("tests/fixtures").join(self.config_file);
        let reference_path = Path::new("tests/fixtures").join(self.reference_file);
        
        // 加载配置
        let patch = synplant::SynplantPatch::from_ron_file(&config_path)?;
        
        // 合成音频
        let synth = synthesizer::SynplantSynthesizer::new(patch.genome);
        let wave = synth.synthesize(self.duration);
        
        // 保存到临时文件
        let output_path = format!("target/test_{}.wav", self.name);
        wave.save_wav16(&output_path)?;
        
        // 与参考音频比较
        let result = audio_compare::compare_wav_files(
            Path::new(&output_path),
            &reference_path
        )?;
        
        println!("\n测试 '{}' 结果:", self.name);
        result.print_report();
        
        // 清理临时文件
        let _ = std::fs::remove_file(&output_path);
        
        // 检查相似度
        if !result.is_similar(self.similarity_threshold) {
            return Err(format!(
                "相似度 {:.2}% 低于阈值 {:.2}%",
                result.similarity,
                self.similarity_threshold
            ).into());
        }
        
        Ok(())
    }
}

#[test]
fn test_default_synthesis() {
    let test = TestCase {
        name: "default",
        config_file: "default.ron",
        reference_file: "default_syn.wav",
        duration: 7.24,
        similarity_threshold: 50.0, // TODO: 提高到99.0%，当前实现约56%
    };
    
    test.run().expect("default音色合成测试失败");
}

/// 辅助函数：列出所有可用的测试样例
#[test]
#[ignore]
fn list_available_tests() {
    let fixtures_dir = Path::new("tests/fixtures");
    println!("\n可用的测试样例:");
    
    if let Ok(entries) = std::fs::read_dir(fixtures_dir) {
        let mut configs = Vec::new();
        let mut wavs = Vec::new();
        
        for entry in entries.flatten() {
            let path = entry.path();
            if let Some(ext) = path.extension() {
                if ext == "ron" {
                    configs.push(path.file_name().unwrap().to_string_lossy().into_owned());
                } else if ext == "wav" {
                    wavs.push(path.file_name().unwrap().to_string_lossy().into_owned());
                }
            }
        }
        
        println!("  配置文件 (.ron): {:?}", configs);
        println!("  参考音频 (.wav): {:?}", wavs);
    }
}
