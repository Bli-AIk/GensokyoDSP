use gensokyo_dsp::*;
use std::path::Path;

/// 测试配置
struct TestCase {
    name: &'static str,
    config_file: &'static str,
    reference_file: &'static str,
    duration: f64,
    folder: &'static str,
}

impl TestCase {
    fn run(&self) -> Result<(), Box<dyn std::error::Error>> {
        let config_path = Path::new("tests/fixtures").join(self.folder).join(self.config_file);
        let reference_path = Path::new("tests/fixtures").join(self.folder).join(self.reference_file);

        // 加载配置
        let patch = synplant::SynplantPatch::from_ron_file(&config_path)?;

        // 合成音频
        let synth = synthesizer::SynplantSynthesizer::new(patch.genome);
        let wave = synth.synthesize(self.duration);

        // 保存到测试输出文件夹
        std::fs::create_dir_all("tests/output")?;
        let output_path = format!("tests/output/test_{}.wav", self.name);
        wave.save_wav16(&output_path)?;

        // 与参考音频比较
        let result = audio_compare::compare_wav_files(Path::new(&output_path), &reference_path)?;

        println!("\n测试 '{}' 结果:", self.name);
        result.print_report();

        // 检查相似度 (硬编码为95%)
        const SIMILARITY_THRESHOLD: f64 = 95.0;
        if !result.is_similar(SIMILARITY_THRESHOLD) {
            return Err(format!(
                "相似度 {:.2}% 低于阈值 {:.2}%",
                result.similarity, SIMILARITY_THRESHOLD
            )
            .into());
        }

        Ok(())
    }
}

#[test]
fn test_vol_atk_0_0547() {
    let test = TestCase {
        name: "vol_atk_0_0547",
        config_file: "vol_atk_0.0547.ron",
        reference_file: "vol_atk_0.0547.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_0547 failed");
} 

#[test]
fn test_vol_atk_0_1058() {
    let test = TestCase {
        name: "vol_atk_0_1058",
        config_file: "vol_atk_0.1058.ron",
        reference_file: "vol_atk_0.1058.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_1058 failed");
} 

#[test]
fn test_vol_atk_0_1496() {
    let test = TestCase {
        name: "vol_atk_0_1496",
        config_file: "vol_atk_0.1496.ron",
        reference_file: "vol_atk_0.1496.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_1496 failed");
} 

#[test]
fn test_vol_atk_0_2007() {
    let test = TestCase {
        name: "vol_atk_0_2007",
        config_file: "vol_atk_0.2007.ron",
        reference_file: "vol_atk_0.2007.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_2007 failed");
} 

#[test]
fn test_vol_atk_0_2518() {
    let test = TestCase {
        name: "vol_atk_0_2518",
        config_file: "vol_atk_0.2518.ron",
        reference_file: "vol_atk_0.2518.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_2518 failed");
} 

#[test]
fn test_vol_atk_0_3102() {
    let test = TestCase {
        name: "vol_atk_0_3102",
        config_file: "vol_atk_0.3102.ron",
        reference_file: "vol_atk_0.3102.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_3102 failed");
} 

#[test]
fn test_vol_atk_0_3540() {
    let test = TestCase {
        name: "vol_atk_0_3540",
        config_file: "vol_atk_0.3540.ron",
        reference_file: "vol_atk_0.3540.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_3540 failed");
} 

#[test]
fn test_vol_atk_0_4051() {
    let test = TestCase {
        name: "vol_atk_0_4051",
        config_file: "vol_atk_0.4051.ron",
        reference_file: "vol_atk_0.4051.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_4051 failed");
} 

#[test]
fn test_vol_atk_0_4536() {
    let test = TestCase {
        name: "vol_atk_0_4536",
        config_file: "vol_atk_0.4536.ron",
        reference_file: "vol_atk_0.4536.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_4536 failed");
} 

#[test]
fn test_vol_atk_0_4958() {
    let test = TestCase {
        name: "vol_atk_0_4958",
        config_file: "vol_atk_0.4958.ron",
        reference_file: "vol_atk_0.4958.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_4958 failed");
} 

#[test]
fn test_vol_atk_0_5506() {
    let test = TestCase {
        name: "vol_atk_0_5506",
        config_file: "vol_atk_0.5506.ron",
        reference_file: "vol_atk_0.5506.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_5506 failed");
} 

#[test]
fn test_vol_atk_0_6055() {
    let test = TestCase {
        name: "vol_atk_0_6055",
        config_file: "vol_atk_0.6055.ron",
        reference_file: "vol_atk_0.6055.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_6055 failed");
} 

#[test]
fn test_vol_atk_0_6519() {
    let test = TestCase {
        name: "vol_atk_0_6519",
        config_file: "vol_atk_0.6519.ron",
        reference_file: "vol_atk_0.6519.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_6519 failed");
} 

#[test]
fn test_vol_atk_0_7025() {
    let test = TestCase {
        name: "vol_atk_0_7025",
        config_file: "vol_atk_0.7025.ron",
        reference_file: "vol_atk_0.7025.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_7025 failed");
} 

#[test]
fn test_vol_atk_0_7489() {
    let test = TestCase {
        name: "vol_atk_0_7489",
        config_file: "vol_atk_0.7489.ron",
        reference_file: "vol_atk_0.7489.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_7489 failed");
} 

#[test]
fn test_vol_atk_0_8080() {
    let test = TestCase {
        name: "vol_atk_0_8080",
        config_file: "vol_atk_0.8080.ron",
        reference_file: "vol_atk_0.8080.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_8080 failed");
} 

#[test]
fn test_vol_atk_0_8502() {
    let test = TestCase {
        name: "vol_atk_0_8502",
        config_file: "vol_atk_0.8502.ron",
        reference_file: "vol_atk_0.8502.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_8502 failed");
} 

#[test]
fn test_vol_atk_0_9051() {
    let test = TestCase {
        name: "vol_atk_0_9051",
        config_file: "vol_atk_0.9051.ron",
        reference_file: "vol_atk_0.9051.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_9051 failed");
} 

#[test]
fn test_vol_atk_0_9515() {
    let test = TestCase {
        name: "vol_atk_0_9515",
        config_file: "vol_atk_0.9515.ron",
        reference_file: "vol_atk_0.9515.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_0_9515 failed");
} 

#[test]
fn test_vol_atk_1_0() {
    let test = TestCase {
        name: "vol_atk_1_0",
        config_file: "vol_atk_1.0.ron",
        reference_file: "vol_atk_1.0.wav",
        duration: 7.24,
        folder: "vol_atk_tests",
    };
    test.run().expect("test_vol_atk_1_0 failed");
} 

#[test]
fn test_vol_sus_0_0() {
    let test = TestCase {
        name: "vol_sus_0_0",
        config_file: "vol_sus_0.0.ron",
        reference_file: "vol_sus_0.0.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_0 failed");
} 

#[test]
fn test_vol_sus_0_0547() {
    let test = TestCase {
        name: "vol_sus_0_0547",
        config_file: "vol_sus_0.0547.ron",
        reference_file: "vol_sus_0.0547.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_0547 failed");
} 

#[test]
fn test_vol_sus_0_1058() {
    let test = TestCase {
        name: "vol_sus_0_1058",
        config_file: "vol_sus_0.1058.ron",
        reference_file: "vol_sus_0.1058.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_1058 failed");
} 

#[test]
fn test_vol_sus_0_1496() {
    let test = TestCase {
        name: "vol_sus_0_1496",
        config_file: "vol_sus_0.1496.ron",
        reference_file: "vol_sus_0.1496.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_1496 failed");
} 

#[test]
fn test_vol_sus_0_2007() {
    let test = TestCase {
        name: "vol_sus_0_2007",
        config_file: "vol_sus_0.2007.ron",
        reference_file: "vol_sus_0.2007.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_2007 failed");
} 

#[test]
fn test_vol_sus_0_2518() {
    let test = TestCase {
        name: "vol_sus_0_2518",
        config_file: "vol_sus_0.2518.ron",
        reference_file: "vol_sus_0.2518.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_2518 failed");
} 

#[test]
fn test_vol_sus_0_3102() {
    let test = TestCase {
        name: "vol_sus_0_3102",
        config_file: "vol_sus_0.3102.ron",
        reference_file: "vol_sus_0.3102.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_3102 failed");
} 

#[test]
fn test_vol_sus_0_3540() {
    let test = TestCase {
        name: "vol_sus_0_3540",
        config_file: "vol_sus_0.3540.ron",
        reference_file: "vol_sus_0.3540.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_3540 failed");
} 

#[test]
fn test_vol_sus_0_4051() {
    let test = TestCase {
        name: "vol_sus_0_4051",
        config_file: "vol_sus_0.4051.ron",
        reference_file: "vol_sus_0.4051.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_4051 failed");
} 

#[test]
fn test_vol_sus_0_4536() {
    let test = TestCase {
        name: "vol_sus_0_4536",
        config_file: "vol_sus_0.4536.ron",
        reference_file: "vol_sus_0.4536.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_4536 failed");
} 

#[test]
fn test_vol_sus_0_4958() {
    let test = TestCase {
        name: "vol_sus_0_4958",
        config_file: "vol_sus_0.4958.ron",
        reference_file: "vol_sus_0.4958.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_4958 failed");
} 

#[test]
fn test_vol_sus_0_5506() {
    let test = TestCase {
        name: "vol_sus_0_5506",
        config_file: "vol_sus_0.5506.ron",
        reference_file: "vol_sus_0.5506.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_5506 failed");
} 

#[test]
fn test_vol_sus_0_6055() {
    let test = TestCase {
        name: "vol_sus_0_6055",
        config_file: "vol_sus_0.6055.ron",
        reference_file: "vol_sus_0.6055.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_6055 failed");
} 

#[test]
fn test_vol_sus_0_6519() {
    let test = TestCase {
        name: "vol_sus_0_6519",
        config_file: "vol_sus_0.6519.ron",
        reference_file: "vol_sus_0.6519.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_6519 failed");
} 

#[test]
fn test_vol_sus_0_7025() {
    let test = TestCase {
        name: "vol_sus_0_7025",
        config_file: "vol_sus_0.7025.ron",
        reference_file: "vol_sus_0.7025.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_7025 failed");
} 

#[test]
fn test_vol_sus_0_7489() {
    let test = TestCase {
        name: "vol_sus_0_7489",
        config_file: "vol_sus_0.7489.ron",
        reference_file: "vol_sus_0.7489.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_7489 failed");
} 

#[test]
fn test_vol_sus_0_8080() {
    let test = TestCase {
        name: "vol_sus_0_8080",
        config_file: "vol_sus_0.8080.ron",
        reference_file: "vol_sus_0.8080.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_8080 failed");
} 

#[test]
fn test_vol_sus_0_8502() {
    let test = TestCase {
        name: "vol_sus_0_8502",
        config_file: "vol_sus_0.8502.ron",
        reference_file: "vol_sus_0.8502.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_8502 failed");
} 

#[test]
fn test_vol_sus_0_9051() {
    let test = TestCase {
        name: "vol_sus_0_9051",
        config_file: "vol_sus_0.9051.ron",
        reference_file: "vol_sus_0.9051.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_9051 failed");
} 

#[test]
fn test_vol_sus_0_9515() {
    let test = TestCase {
        name: "vol_sus_0_9515",
        config_file: "vol_sus_0.9515.ron",
        reference_file: "vol_sus_0.9515.wav",
        duration: 7.24,
        folder: "vol_sus_tests",
    };
    test.run().expect("test_vol_sus_0_9515 failed");
} 