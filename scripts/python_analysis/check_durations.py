#!/usr/bin/env python3
"""
检查参考文件和输出文件的时长差异
"""
import wave
from pathlib import Path

def get_wav_duration(filepath):
    """获取WAV文件时长"""
    with wave.open(str(filepath), 'rb') as w:
        frames = w.getnframes()
        rate = w.getframerate()
        duration = frames / float(rate)
        return duration, frames, rate

def main():
    # 检查a_color测试文件
    fixtures = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures/a_color_tests")
    output = Path("/home/aik/rustProjects/GensokyoDSP/tests/output")
    
    print("检查 a_color 测试文件时长:")
    print("="*60)
    
    for ref_file in sorted(fixtures.glob("a_color_*.wav")):
        test_name = ref_file.stem
        output_file = output / f"test_{test_name}.wav"
        
        ref_dur, ref_frames, ref_rate = get_wav_duration(ref_file)
        
        if output_file.exists():
            out_dur, out_frames, out_rate = get_wav_duration(output_file)
            diff = abs(out_dur - ref_dur)
            
            print(f"\n{test_name}:")
            print(f"  参考: {ref_dur:.4f}s ({ref_frames} frames @ {ref_rate}Hz)")
            print(f"  输出: {out_dur:.4f}s ({out_frames} frames @ {out_rate}Hz)")
            print(f"  差异: {diff:.4f}s ({abs(out_frames - ref_frames)} frames)")
        else:
            print(f"\n{test_name}:")
            print(f"  参考: {ref_dur:.4f}s ({ref_frames} frames @ {ref_rate}Hz)")
            print(f"  输出: 不存在")
    
    # 检查其他分类的一些文件
    print("\n\n检查其他测试类别:")
    print("="*60)
    
    categories = ["a_form_tests", "a_freq_tests", "vol_atk_tests"]
    
    for cat in categories:
        cat_path = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures") / cat
        if not cat_path.exists():
            continue
        
        # 只检查第一个文件
        wav_files = sorted(cat_path.glob("*.wav"))
        if wav_files:
            ref_file = wav_files[0]
            test_name = ref_file.stem
            output_file = output / f"test_{test_name}.wav"
            
            ref_dur, ref_frames, ref_rate = get_wav_duration(ref_file)
            
            print(f"\n{cat}/{test_name}:")
            print(f"  参考: {ref_dur:.4f}s ({ref_frames} frames @ {ref_rate}Hz)")
            
            if output_file.exists():
                out_dur, out_frames, out_rate = get_wav_duration(output_file)
                diff = abs(out_dur - ref_dur)
                print(f"  输出: {out_dur:.4f}s ({out_frames} frames @ {out_rate}Hz)")
                print(f"  差异: {diff:.4f}s ({abs(out_frames - ref_frames)} frames)")

if __name__ == "__main__":
    main()
