use gensokyo_dsp::*;
use std::env;
use std::path::{Path, PathBuf};

fn print_usage() {
    println!("用法:");
    println!("  gensokyo_dsp <配置文件.ron> [输出文件.wav] [持续时间(秒)] [参考文件.wav]");
    println!();
    println!("参数:");
    println!("  <配置文件.ron>     - 必需: Synplant配置文件路径");
    println!("  [输出文件.wav]     - 可选: 输出WAV文件路径 (默认: output.wav)");
    println!("  [持续时间(秒)]     - 可选: 音频持续时间 (默认: 5.0)");
    println!("  [参考文件.wav]     - 可选: 参考音频文件，用于比较相似度");
    println!();
    println!("示例:");
    println!("  gensokyo_dsp assets/default.ron");
    println!("  gensokyo_dsp assets/default.ron output_default.wav 7.24");
    println!("  gensokyo_dsp assets/default.ron output.wav 7.24 reference.wav");
}

fn synthesize_from_config(
    config_path: &Path,
    output_path: &Path,
    duration: f64,
    reference_path: Option<&Path>
) -> Result<(), Box<dyn std::error::Error>> {
    // 加载配置
    let patch = synplant::SynplantPatch::from_ron_file(config_path)?;
    println!("  已加载音色: {}", patch.name);
    
    // 合成音频
    let synth = synthesizer::SynplantSynthesizer::new(patch.genome);
    let wave = synth.synthesize(duration);
    
    // 保存文件
    wave.save_wav16(output_path)?;
    println!("  ✓ 已保存到: {}", output_path.display());
    
    // 如果有参考文件，进行比较
    if let Some(ref_path) = reference_path {
        if ref_path.exists() {
            println!("\n  与参考音频比较:");
            match compare_wav_files(output_path, ref_path) {
                Ok(result) => {
                    result.print_report();
                    if result.similarity >= 99.0 {
                        println!("  ✓ 相似度达标");
                    } else {
                        println!("  ⚠ 相似度未达到99%目标");
                    }
                }
                Err(e) => eprintln!("  比较失败: {}", e),
            }
        } else {
            eprintln!("  ⚠ 参考文件不存在: {}", ref_path.display());
        }
    }
    
    Ok(())
}

fn main() {
    println!("=== Gensokyo DSP - Synplant音色合成器 ===\n");
    
    let args: Vec<String> = env::args().collect();
    
    // 如果没有参数，显示帮助并使用默认配置
    if args.len() < 2 {
        println!("未指定配置文件，使用默认配置...\n");
        
        let config_path = Path::new("assets/default.ron");
        let output_path = Path::new("output_default.wav");
        let duration = 7.24;
        let reference_path = Path::new("tests/fixtures/default_syn.wav");
        
        if !config_path.exists() {
            eprintln!("错误: 默认配置文件不存在: {}", config_path.display());
            eprintln!("\n请指定配置文件:");
            print_usage();
            std::process::exit(1);
        }
        
        println!("正在合成音色...");
        match synthesize_from_config(
            config_path,
            output_path,
            duration,
            if reference_path.exists() { Some(reference_path) } else { None }
        ) {
            Ok(_) => println!("\n✓ 合成完成！"),
            Err(e) => {
                eprintln!("\n✗ 合成失败: {}", e);
                std::process::exit(1);
            }
        }
        return;
    }
    
    // 解析命令行参数
    let config_path = PathBuf::from(&args[1]);
    let output_path = if args.len() > 2 {
        PathBuf::from(&args[2])
    } else {
        PathBuf::from("output.wav")
    };
    let duration: f64 = if args.len() > 3 {
        args[3].parse().unwrap_or_else(|_| {
            eprintln!("错误: 无效的持续时间参数: {}", args[3]);
            std::process::exit(1);
        })
    } else {
        5.0
    };
    let reference_path = if args.len() > 4 {
        Some(PathBuf::from(&args[4]))
    } else {
        None
    };
    
    // 验证配置文件存在
    if !config_path.exists() {
        eprintln!("错误: 配置文件不存在: {}", config_path.display());
        std::process::exit(1);
    }
    
    println!("正在合成音色...");
    match synthesize_from_config(
        &config_path,
        &output_path,
        duration,
        reference_path.as_deref()
    ) {
        Ok(_) => println!("\n✓ 合成完成！"),
        Err(e) => {
            eprintln!("\n✗ 合成失败: {}", e);
            std::process::exit(1);
        }
    }
}
