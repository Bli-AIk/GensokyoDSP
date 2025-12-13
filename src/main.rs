mod synplant;
mod synthesizer;
mod audio_compare;

use synplant::SynplantPatch;
use synthesizer::SynplantSynthesizer;
use audio_compare::compare_wav_files;
use std::path::Path;

fn main() {
    println!("=== Gensokyo DSP - Synplant音色合成器 ===\n");
    
    // 加载并合成default音色
    println!("正在合成 default 音色...");
    match SynplantPatch::from_ron_file("assets/default.ron") {
        Ok(patch) => {
            println!("  已加载: {}", patch.name);
            let synth = SynplantSynthesizer::new(patch.genome);
            // default_syn.wav 持续时间为 7.24秒
            let wave = synth.synthesize(7.24, 48000.0);
            
            match wave.save_wav16("output_default.wav") {
                Ok(_) => {
                    println!("  ✓ 已保存到: output_default.wav");
                    
                    // 与参考音频比较
                    if Path::new("dev/examples/default_syn.wav").exists() {
                        println!("\n  与参考音频比较:");
                        match compare_wav_files(
                            Path::new("output_default.wav"),
                            Path::new("dev/examples/default_syn.wav")
                        ) {
                            Ok(result) => result.print_report(),
                            Err(e) => eprintln!("  比较失败: {}", e),
                        }
                    }
                    println!();
                }
                Err(e) => eprintln!("  ✗ 保存失败: {}\n", e),
            }
        }
        Err(e) => eprintln!("  ✗ 加载失败: {}\n", e),
    }
    
    println!("合成完成！");
}
