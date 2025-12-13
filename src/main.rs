mod synplant;
mod synthesizer;
mod audio_compare;

use synplant::SynplantPatch;
use synthesizer::SynplantSynthesizer;
use audio_compare::compare_wav_files;
use std::path::Path;

fn main() {
    println!("=== Gensokyo DSP - Synplant音色合成器 ===\n");
    
    // 加载并合成koto音色
    println!("正在合成 koto 音色...");
    match SynplantPatch::from_ron_file("assets/koto.ron") {
        Ok(patch) => {
            println!("  已加载: {}", patch.name);
            let synth = SynplantSynthesizer::new(patch.genome);
            let wave = synth.synthesize(5.0, 44100.0);
            
            match wave.save_wav16("output_koto.wav") {
                Ok(_) => {
                    println!("  ✓ 已保存到: output_koto.wav");
                    
                    // 与参考音频比较
                    if Path::new("dev/examples/koto_synthetic.wav").exists() {
                        println!("\n  与参考音频比较:");
                        match compare_wav_files(
                            Path::new("output_koto.wav"),
                            Path::new("dev/examples/koto_synthetic.wav")
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
    
    // 加载并合成zunpet音色
    println!("正在合成 zunpet 音色...");
    match SynplantPatch::from_ron_file("assets/zunpet.ron") {
        Ok(patch) => {
            println!("  已加载: {}", patch.name);
            let synth = SynplantSynthesizer::new(patch.genome);
            let wave = synth.synthesize(5.0, 44100.0);
            
            match wave.save_wav16("output_zunpet.wav") {
                Ok(_) => {
                    println!("  ✓ 已保存到: output_zunpet.wav");
                    
                    // 与参考音频比较
                    if Path::new("dev/examples/zun_pet_syn.wav").exists() {
                        println!("\n  与参考音频比较:");
                        match compare_wav_files(
                            Path::new("output_zunpet.wav"),
                            Path::new("dev/examples/zun_pet_syn.wav")
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
