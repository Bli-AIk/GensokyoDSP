use gensokyo_dsp::*;
use std::path::Path;

/// 测试配置
struct TestCase {
    name: String,
    config_file: String,
    reference_file: String,
    duration: f64,
    folder: &'static str,
    threshold: f64,
}

impl TestCase {
    fn run(&self) -> Result<(), Box<dyn std::error::Error>> {
        let config_path = Path::new("tests/fixtures").join(self.folder).join(&self.config_file);
        let reference_path = Path::new("tests/fixtures").join(self.folder).join(&self.reference_file);

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

        // 检查相似度
        if !result.is_similar(self.threshold) {
            return Err(format!(
                "相似度 {:.2}% 低于阈值 {:.2}%",
                result.similarity, self.threshold
            )
            .into());
        }

        Ok(())
    }
}

macro_rules! generate_tests {
    ($folder:expr, $prefix:expr, $thresh:expr) => {
        #[test]
        fn test_batch() {
            let folder = $folder;
            let prefix = $prefix;
            let threshold = $thresh;
            let dir = Path::new("tests/fixtures").join(folder);
            
            let mut failed = Vec::new();
            
            if let Ok(entries) = std::fs::read_dir(dir) {
                for entry in entries.flatten() {
                    let path = entry.path();
                    if let Some(ext) = path.extension() {
                        if ext == "ron" {
                            let filename = path.file_name().unwrap().to_string_lossy();
                            let name = filename.replace(".ron", "");
                            let ref_file = filename.replace(".ron", ".wav");
                            
                            let test = TestCase {
                                name: name.clone(),
                                config_file: filename.to_string(),
                                reference_file: ref_file,
                                duration: 7.24,
                                folder: folder,
                                threshold: threshold,
                            };
                            
                            print!("Running {}... ", name);
                            match test.run() {
                                Ok(_) => println!("PASS"),
                                Err(e) => {
                                    println!("FAIL: {}", e);
                                    failed.push(name);
                                }
                            }
                        }
                    }
                }
            }
            
            if !failed.is_empty() {
                panic!("Failed tests: {:?}", failed);
            }
        }
    };
}

mod vol_atk {
    use super::*;
    generate_tests!("vol_atk_tests", "vol_atk", 95.0);
}

mod vol_sus {
    use super::*;
    generate_tests!("vol_sus_tests", "vol_sus", 45.0);
}
