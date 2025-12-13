use gensokyo_dsp::*;
use std::path::Path;

/// 测试配置
struct TestCase {
    name: &'static str,
    config_file: &'static str,
    reference_file: &'static str,
    duration: f64,
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
        
        // 检查相似度 (硬编码为95%)
        const SIMILARITY_THRESHOLD: f64 = 95.0;
        if !result.is_similar(SIMILARITY_THRESHOLD) {
            return Err(format!(
                "相似度 {:.2}% 低于阈值 {:.2}%",
                result.similarity,
                SIMILARITY_THRESHOLD
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
    };
    
    test.run().expect("default音色合成测试失败");
}

// a_form波形变形测试 - 正弦波到锯齿波阶段 (0.0 -> 0.57)
#[test]
fn test_a_form_0_1() {
    let test = TestCase {
        name: "a_form_0.1",
        config_file: "a_form_0.1.ron",
        reference_file: "a_form_0.1.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.1 测试失败");
}

#[test]
fn test_a_form_0_2() {
    let test = TestCase {
        name: "a_form_0.2",
        config_file: "a_form_0.2.ron",
        reference_file: "a_form_0.2.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.2 测试失败");
}

#[test]
fn test_a_form_0_3() {
    let test = TestCase {
        name: "a_form_0.3",
        config_file: "a_form_0.3.ron",
        reference_file: "a_form_0.3.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.3 测试失败");
}

#[test]
fn test_a_form_0_4() {
    let test = TestCase {
        name: "a_form_0.4",
        config_file: "a_form_0.4.ron",
        reference_file: "a_form_0.4.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.4 测试失败");
}

#[test]
fn test_a_form_0_5() {
    let test = TestCase {
        name: "a_form_0.5",
        config_file: "a_form_0.5.ron",
        reference_file: "a_form_0.5.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.5 测试失败");
}

// a_form波形变形测试 - 锯齿波到方波阶段 (0.57 -> 0.81)
#[test]
fn test_a_form_0_6() {
    let test = TestCase {
        name: "a_form_0.6",
        config_file: "a_form_0.6.ron",
        reference_file: "a_form_0.6.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.6 测试失败");
}

#[test]
fn test_a_form_0_7() {
    let test = TestCase {
        name: "a_form_0.7",
        config_file: "a_form_0.7.ron",
        reference_file: "a_form_0.7.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.7 测试失败");
}

// a_form波形变形测试 - 方波到脉冲波阶段 (0.81 -> 1.0)
#[test]
fn test_a_form_0_8() {
    let test = TestCase {
        name: "a_form_0.8",
        config_file: "a_form_0.8.ron",
        reference_file: "a_form_0.8.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.8 测试失败");
}

#[test]
fn test_a_form_0_9() {
    let test = TestCase {
        name: "a_form_0.9",
        config_file: "a_form_0.9.ron",
        reference_file: "a_form_0.9.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=0.9 测试失败");
}

#[test]
fn test_a_form_1_0() {
    let test = TestCase {
        name: "a_form_1.0",
        config_file: "a_form_1.0.ron",
        reference_file: "a_form_1.0.wav",
        duration: 7.24,
    };
    test.run().expect("a_form=1.0 测试失败");
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
